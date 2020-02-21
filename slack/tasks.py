import logging
import traceback

from celery import shared_task
from django.conf import settings

from frisky.bot import Frisky
from frisky.events import ReactionEvent, MessageEvent
from frisky.responses import FriskyResponse, Image
from slack.api.client import SlackApiClient
from slack.api.models import Event, ReactionAdded, MessageSent, Conversation

logger = logging.getLogger(__name__)

SUBTYPE_BLACKLIST = ['bot_message', 'message_deleted']

slack_api_client = SlackApiClient(settings.SLACK_ACCESS_TOKEN)

frisky = Frisky(
    name=settings.FRISKY_NAME,
    prefix=settings.FRISKY_PREFIX,
    ignored_channels=settings.FRISKY_IGNORED_CHANNELS,
)


def reply_channel(conversation: Conversation, response: FriskyResponse) -> bool:
    if isinstance(response, str):
        return slack_api_client.post_message(conversation, response)
    if isinstance(response, Image):
        return slack_api_client.post_image(conversation, response.url, response.alt_text)
    return False


def handle_message_event(event: MessageSent):
    user = slack_api_client.get_user(event.user)
    if event.channel_type == 'im':
        # TODO: Is there an api method (or a reason) to look this up?
        channel = Conversation(id=event.channel, name=user.name)
    elif event.channel_type == 'channel':
        channel = slack_api_client.get_channel(event.channel)
    else:
        return
    frisky.handle_message(
        MessageEvent(
            username=user.get_short_name(),
            channel_name=channel.name,
            text=event.text,
            command='',
            args=tuple(),
        ),
        reply_channel=lambda reply: reply_channel(channel, reply)
    )


def handle_reaction_event(event: ReactionAdded):
    user = slack_api_client.get_user(event.user)
    channel = slack_api_client.get_channel(event.item.channel)
    item_user = slack_api_client.get_user(event.item_user)
    added = event.type == 'reaction_added'
    message = slack_api_client.get_message(channel, event.item.ts)

    frisky.handle_reaction(
        ReactionEvent(
            emoji=event.reaction,
            username=user.get_short_name(),
            added=added,
            message=MessageEvent(
                username=item_user.get_short_name(),
                channel_name=channel.name,
                text=message.text if message is not None else "",
                command='',
                args=tuple(),
            ),
        ),
        reply_channel=lambda reply: slack_api_client.post_message(channel, reply)
    )


def sanitize(data: dict): dict


@shared_task
def process_event(data):
    logger.debug(f'Handling event from slack: ')
    if data['event'].get('subtype') in SUBTYPE_BLACKLIST:
        logger.debug(f'Ignoring {data["event"]["event_id"]}, subtype was in blacklist')
        return

    # noinspection PyBroadException
    try:
        event_wrapper: Event = Event.from_dict(data)
        event = event_wrapper.get_event()

        if isinstance(event, MessageSent):
            handle_message_event(event)
        elif isinstance(event, ReactionAdded):
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
