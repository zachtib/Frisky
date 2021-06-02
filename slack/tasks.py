import logging
from dataclasses import dataclass
from typing import Optional

from celery import shared_task
from django.conf import settings

from frisky.models import Workspace, Channel, Member
from slack.api.models import Event, ReactionAdded, MessageSent
from slack.errors import UnsupportedSlackEventTypeError
from slack.wrapper import SlackWrapper

logger = logging.getLogger(__name__)

SUBTYPE_BLACKLIST = ['bot_message', 'message_changed', 'message_deleted']


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
    try:
        team_id = data['team_id']
        event_id = data['event_id']
        event = data['event']
        channel_id = event.get('channel') or event['item']['channel']
        user_id = event['user']
        event_type = event['type']
        event_subtype = event.get('subtype', None)
        item_user = event.get('item_user', None)
    except KeyError as err:
        logger.warning(f'Encountered a KeyError while processing:\n{data}', exc_info=err)
        return

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
