import logging
import re
from typing import Optional

from django.conf import settings

from frisky.bot import Frisky
from frisky.events import MessageEvent, ReactionEvent
from frisky.models import Workspace, Channel, Member
from frisky.responses import FriskyResponse, Image
from slack.api.client import SlackApiClient
from slack.api.models import Conversation, ReactionAdded, MessageSent
from slack.events import SlackEvent, ReactionAddedEvent, ReactionRemovedEvent, MessageSentEvent

logger = logging.getLogger(__name__)

frisky = Frisky(
    name=settings.FRISKY_NAME,
    prefix=settings.FRISKY_PREFIX,
    ignored_channels=settings.FRISKY_IGNORED_CHANNELS,
)


class SlackWrapper:
    USER_ID_PATTERN = re.compile(r'<@(?P<user_id>\w+)>')

    def __init__(self, workspace: Workspace, channel: Channel, sender: Member):
        self.frisky = Frisky(
            name=settings.FRISKY_NAME,
            prefix=settings.FRISKY_PREFIX,
            ignored_channels=settings.FRISKY_IGNORED_CHANNELS,
        )
        self.workspace = workspace
        self.channel = channel
        self.sender = sender
        self.users = {
            sender.user_id: sender,
        }
        self.slack_api_client = SlackApiClient(self.workspace.access_token)

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

        if self.channel.is_private:
            # We don't grab message contents for private channels
            message_text = None
        else:
            message = self.slack_api_client.get_message(Conversation(id=self.channel.channel_id), event.item.ts)
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

    def get_message_text(self, timestamp) -> Optional[str]:
        if not self.channel.is_private:
            message = self.slack_api_client.get_message_by_timestamp(self.channel.channel_id, timestamp)
            if message is not None:
                if len(message.text) > 0:
                    # Message contains text
                    return message.text
                elif message.files is not None and len(message.files) > 0:
                    # Message has no text, but it does have attachments. Maybe revisit this
                    return message.files[0].permalink
        return None

    def create_frisky_reaction_added_event(self, event: ReactionAddedEvent) -> ReactionEvent:
        item_user = Member.objects.get_or_fetch_by_workspace_and_id(self.workspace, event.item_user_id)
        message_text = self.get_message_text(event.item_ts)

        return ReactionEvent(
            workspace=self.workspace,
            channel=self.channel,
            user=self.sender,
            users=self.users,
            emoji=event.reaction,
            username=self.sender.name,
            added=True,
            message=self.construct_frisky_message_event(
                message_text=message_text,
                override_sender=item_user
            ),
        )

    def create_frisky_reaction_removed_event(self, event: ReactionRemovedEvent) -> ReactionEvent:
        item_user = Member.objects.get_or_fetch_by_workspace_and_id(self.workspace, event.item_user_id)
        message_text = self.get_message_text(event.item_ts)

        return ReactionEvent(
            workspace=self.workspace,
            channel=self.channel,
            user=self.sender,
            users=self.users,
            emoji=event.reaction,
            username=self.sender.name,
            added=False,
            message=self.construct_frisky_message_event(
                message_text=message_text,
                override_sender=item_user
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

    def handle_event(self, event: SlackEvent):
        if isinstance(event, ReactionAddedEvent):
            frisky.handle_reaction(
                self.create_frisky_reaction_added_event(event),
                reply_channel=lambda response: self.reply(response)
            )
        elif isinstance(event, ReactionRemovedEvent):
            frisky.handle_reaction(
                self.create_frisky_reaction_removed_event(event),
                reply_channel=lambda response: self.reply(response)
            )
        elif isinstance(event, MessageSentEvent):
            if not event.text.startswith(settings.FRISKY_PREFIX):
                return
            frisky.handle_message(
                self.construct_frisky_message_event(event.text),
                reply_channel=lambda response: self.reply(response)
            )
        else:
            logger.warning(f"Asked to handle an unsupported event type: {type(event)}")
