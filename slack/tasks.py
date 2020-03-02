import logging
import re
import traceback
from typing import Pattern, Match

from celery import shared_task
from django.conf import settings

from frisky.bot import Frisky
from frisky.events import ReactionEvent, MessageEvent
from frisky.responses import FriskyResponse, Image
from slack.api.client import SlackApiClient
from slack.api.models import Event, ReactionAdded, MessageSent, Conversation

logger = logging.getLogger(__name__)

SUBTYPE_BLACKLIST = ['bot_message', 'message_changed', 'message_deleted']

slack_api_client = SlackApiClient(settings.SLACK_ACCESS_TOKEN)

frisky = Frisky(
    name=settings.FRISKY_NAME,
    prefix=settings.FRISKY_PREFIX,
    ignored_channels=settings.FRISKY_IGNORED_CHANNELS,
)

username_pattern: Pattern[str] = re.compile(r'<@(?P<user_id>\w+)>')


def replace_usernames(match: Match[str]) -> str:
    user_id = match.group('user_id')
    user = slack_api_client.get_user(user_id)
    if user is None:
        return 'unknown'
    return user.get_short_name()


def sanitize_message_text(text: str) -> str:
    text = username_pattern.sub(replace_usernames, text)
    text = text.replace('“', '"').replace('”', '"')
    return text


def reply_channel(conversation: Conversation, response: FriskyResponse) -> bool:
    if isinstance(response, str):
        return slack_api_client.post_message(conversation, response)
    if isinstance(response, Image):
        return slack_api_client.post_image(conversation, response.url, response.alt_text)
    return False


def handle_message_event(event: MessageSent):
    if not event.text.startswith(settings.FRISKY_PREFIX):
        return

    user = slack_api_client.get_user(event.user)
    channel = slack_api_client.get_channel(event.channel)

    frisky.handle_message(
        MessageEvent(
            username=user.get_short_name(),
            channel_name=channel.name,
            text=sanitize_message_text(event.text),
        ),
        reply_channel=lambda reply: reply_channel(channel, reply)
    )


def handle_reaction_event(event: ReactionAdded):
    user = slack_api_client.get_user(event.user)
    channel = slack_api_client.get_channel(event.item.channel)
    item_user = slack_api_client.get_user(event.item_user)
    added = event.type == 'reaction_added'

    message_text = None
    if not channel.is_private:
        message = slack_api_client.get_message(channel, event.item.ts)
        if message is not None:
            message_text = sanitize_message_text(message.text)
    else:
        logger.debug('Did not query api for message, because we are in a private channel')

    frisky.handle_reaction(
        ReactionEvent(
            emoji=event.reaction,
            username=user.get_short_name(),
            added=added,
            message=MessageEvent(
                username=item_user.get_short_name(),
                channel_name=channel.name,
                text=message_text,
            ),
        ),
        reply_channel=lambda reply: slack_api_client.post_message(channel, reply)
    )


@shared_task
def process_event(data):
    # noinspection PyBroadException
    try:
        event_id = data["event"].get("event_id")
        event_type = data.get('event', {}).get('type')
        event_subtype = data.get('event', {}).get('subtype')
        item_user = data.get('event', {}).get('item_user')
        if event_subtype in SUBTYPE_BLACKLIST:
            return logger.debug(f'Ignoring {event_id}, subtype was in blacklist')
        elif event_type == 'reaction_added' and not item_user:
            return logger.debug(f'Ignoring {event_id}, it had no item_user')
        event_wrapper: Event = Event.from_dict(data)
        event = event_wrapper.get_event()

        if isinstance(event, MessageSent):
            handle_message_event(event)
        elif isinstance(event, ReactionAdded):
            if event.reaction == 'dumpling':
                raw_message = slack_api_client.get_message_raw(event.item.channel, event.item.ts)
                slack_api_client.emergency_log(str(raw_message))
            handle_reaction_event(event)

    except KeyError as err:
        stacktrace = traceback.format_exc()
        slack_api_client.emergency_log(stacktrace)
        slack_api_client.emergency_log(f'Trouble deserializing this event:\n{str(data)}')
        logger.warning('KeyError thrown deserializing event', exc_info=err)
    except Exception as err:
        stacktrace = traceback.format_exc()
        log_message = f'{stacktrace}\nCaused by:\n{str(data)}'
        slack_api_client.emergency_log(log_message)
        logger.warning('General exception thrown handling event', exc_info=err)
