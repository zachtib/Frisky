import logging
import re
from typing import Optional

from celery import shared_task
from django.conf import settings

from frisky.bot import Frisky
from frisky.events import ReactionEvent, MessageEvent
from frisky.models import Workspace, Channel, Member
from frisky.responses import FriskyResponse, Image
from slack.api.client import SlackApiClient
from slack.api.models import Event, ReactionAdded, MessageSent, Conversation

logger = logging.getLogger(__name__)

SUBTYPE_BLACKLIST = ['bot_message', 'message_changed', 'message_deleted']

frisky = Frisky(
    name=settings.FRISKY_NAME,
    prefix=settings.FRISKY_PREFIX,
    ignored_channels=settings.FRISKY_IGNORED_CHANNELS,
)


class SlackWrapper:
    USER_ID_PATTERN = re.compile(r'<@(?P<user_id>\w+)>')

    def __init__(self, workspace: Workspace, channel: Channel, sender: Member):
        self.workspace = workspace
        self.channel = channel
        self.sender = sender
        self.users = {
            sender.user_id: sender,
        }

    def replace_usernames(self, input_string) -> str:
        updated_string: str = input_string
        for user_id in re.findall(self.USER_ID_PATTERN, input_string):
            user = Member.objects.get_or_fetch_by_workspace_and_id(self.workspace, user_id)
            updated_string = updated_string.replace(f'<@{user_id}>', user.name)
            self.users[user_id] = user
        return updated_string

    def clean_message_text(self, text: Optional[str]) -> Optional[str]:
        if text is None:
            return None
        text = text.replace('“', '"').replace('”', '"')
        text = self.replace_usernames(text)
        return text

    def reply(self, response: FriskyResponse) -> bool:
        slack_api_client = SlackApiClient(self.workspace.access_token)
        if isinstance(response, str):
            return slack_api_client.post_message(Conversation(id=self.channel.channel_id), response)
        if isinstance(response, Image):
            return slack_api_client.post_image(Conversation(id=self.channel.channel_id), response.url,
                                               response.alt_text)
        return False

    def construct_frisky_message_event(self, message_text, override_sender: Optional[Member] = None) -> MessageEvent:
        sender_to_use = override_sender or self.sender
        cleaned_text = self.clean_message_text(message_text)
        return MessageEvent(
            workspace=self.workspace,
            channel=self.channel,
            user=sender_to_use,
            users=self.users,
            raw_message=message_text,
            username=sender_to_use.name,
            channel_name=self.channel.name,
            text=cleaned_text,
        )

    def construct_frisky_reaction_event(self, event: ReactionAdded) -> ReactionEvent:
        receiving_user = Member.objects.get_or_fetch_by_workspace_and_id(self.workspace, event.item_user)
        was_added = event.type == 'reaction_added'
        slack_api_client = SlackApiClient(self.workspace.access_token)
        if self.channel.is_private:
            # We don't grab message contents for private channels
            message_text = None
        else:
            message = slack_api_client.get_message(Conversation(id=self.channel.channel_id), event.item.ts)
            if message is not None:
                if len(message.text) > 0:
                    # Message contains text
                    message_text = message.text
                elif message.files is not None and len(message.files) > 0:
                    # Message has no text, but it does have attachments. Maybe revisit this
                    message_text = message.files[0].permalink
                else:
                    # Somehow we have a message, but no text or attachments. Weird.
                    message_text = None
            else:
                # Unable to find message from the api, leave it blank
                message_text = None

        return ReactionEvent(
            workspace=self.workspace,
            channel=self.channel,
            user=self.sender,
            users=self.users,
            emoji=event.reaction,
            username=self.sender.name,
            added=was_added,
            message=self.construct_frisky_message_event(
                message_text=message_text,
                override_sender=receiving_user
            ),
        )

    def handle_message(self, event: MessageSent):
        if not event.text.startswith(settings.FRISKY_PREFIX):
            return
        frisky.handle_message(
            self.construct_frisky_message_event(event.text),
            reply_channel=lambda response: self.reply(response)
        )

    def handle_reaction(self, event: ReactionAdded):
        frisky.handle_reaction(
            self.construct_frisky_reaction_event(event),
            reply_channel=lambda response: self.reply(response)
        )

    def handle_cli(self, command):
        event = self.construct_frisky_message_event(command)
        slack_api_client = SlackApiClient(self.workspace.access_token)
        for reply in frisky.handle_message_synchronously(event):
            if reply is not None:
                slack_api_client.post_message(Conversation(id=self.channel.channel_id), reply)

    def handle_raw(self, text):
        message = self.construct_frisky_message_event(text)
        return frisky.handle_message_synchronously(message)


def process_from_cli(workspace_name, channel_name, username, message):
    if not message.startswith(settings.FRISKY_PREFIX):
        message = f'{settings.FRISKY_PREFIX}{message}'
    workspace = Workspace.objects.get(domain=workspace_name)
    channel = Channel.objects.get(workspace=workspace, name=channel_name)
    user = Member.objects.get(workspace=workspace, name=username)
    wrapper = SlackWrapper(workspace, channel, user)
    wrapper.handle_cli(message)


@shared_task
def process_slack_event(data: dict):
    team_id = data['team_id']
    event_id = data['event_id']
    event = data['event']
    channel_id = event['channel']
    user_id = event['user']
    event_type = event['type']
    event_subtype = event.get('subtype', None)
    item_user = event.get('item_user', None)

    if event_subtype in SUBTYPE_BLACKLIST:
        return logger.debug(f'Ignoring {event_id}, subtype was in blacklist')
    elif event_type == 'reaction_added' and not item_user:
        return logger.debug(f'Ignoring {event_id}, it had no item_user')

    # Now, let's grab our rich Workspace objects
    workspace = Workspace.objects.get_or_fetch_by_kind_and_id(Workspace.Kind.SLACK, team_id)
    channel = Channel.objects.get_or_fetch_by_workspace_and_id(workspace, channel_id)
    member = Member.objects.get_or_fetch_by_workspace_and_id(workspace, user_id)

    event_wrapper: Event = Event.from_dict(data)
    event = event_wrapper.get_event()

    wrapper = SlackWrapper(workspace, channel, member)

    if isinstance(event, MessageSent):
        wrapper.handle_message(event)
    elif isinstance(event, ReactionAdded):
        wrapper.handle_reaction(event)
