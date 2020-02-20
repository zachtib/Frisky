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


def reply(client: SlackApiClient, conversation: Conversation, response: FriskyResponse) -> bool:
    if isinstance(response, str):
        return client.post_message(conversation, response)
    if isinstance(response, Image):
        return client.post_image(conversation, response.url, response.alt_text)
    return False


@shared_task
def process_event(data):
    slack_api_client = SlackApiClient(settings.SLACK_ACCESS_TOKEN)
    # noinspection PyBroadException
    try:
        event_wrapper: Event = Event.from_dict(data)
        event = event_wrapper.get_event()
        # team = slack_api_client.get_workspace(data['team_id'])
        frisky = Frisky(
            name=settings.FRISKY_NAME,
            prefix=settings.FRISKY_PREFIX,
            ignored_channels=settings.FRISKY_IGNORED_CHANNELS,
        )

        if isinstance(event, ReactionAdded):
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
                        text=message.text,
                        command='',
                        args=tuple(),
                    ),
                ),
                reply_channel=lambda reply: slack_api_client.post_message(channel, reply)
            )
        elif isinstance(event, MessageSent):
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
                reply_channel=lambda res: reply(slack_api_client, channel, res)
            )
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
