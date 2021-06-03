import logging

from celery import shared_task
from django.conf import settings

from frisky.models import Workspace, Channel, Member
from slack.events import SlackEventParser
from slack.processor import SlackEventProcessor, EventProperties
from slack.wrapper import SlackWrapper

logger = logging.getLogger(__name__)

SUBTYPE_BLACKLIST = ['bot_message', 'message_changed', 'message_deleted', 'message_replied']


def process_from_cli(workspace_name, channel_name, username, message):
    if not message.startswith(settings.FRISKY_PREFIX):
        message = f'{settings.FRISKY_PREFIX}{message}'
    workspace = Workspace.objects.get(domain=workspace_name)
    channel = Channel.objects.get(workspace=workspace, name=channel_name)
    user = Member.objects.get(workspace=workspace, name=username)
    wrapper = SlackWrapper(workspace, channel, user)
    wrapper.handle_cli(message)


@shared_task
def ingest_from_slack_events_api(payload: dict):
    # First, parse out our common event properties
    processor = SlackEventProcessor()
    properties: EventProperties = processor.parse_event_properties(payload)

    if properties.event_subtype in SUBTYPE_BLACKLIST:
        return logger.debug(f'Ignoring {properties.event_id}, subtype was in blacklist')
    elif properties.event_type in ('reaction_added', 'reaction_removed'):
        if payload['event'].get('item_user', None) is None:
            return logger.debug(f'Ignoring {properties.event_id}, it had no item_user')

    # Now, let's grab our rich Workspace objects
    workspace = Workspace.objects.get_or_fetch_by_kind_and_id(Workspace.Kind.SLACK, properties.team_id)
    channel = Channel.objects.get_or_fetch_by_workspace_and_id(workspace, properties.channel_id)
    member = Member.objects.get_or_fetch_by_workspace_and_id(workspace, properties.user_id)

    parser = SlackEventParser()
    event = parser.parse_event(properties, payload['event'])

    # Now, create the wrapper instance
    wrapper = SlackWrapper(workspace, channel, member)
    # And process the event
    wrapper.handle_event(event)
