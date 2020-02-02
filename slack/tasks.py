from celery import shared_task
from django.conf import settings

from frisky.bot import handle_reaction, handle_message
from slack.api.client import SlackApiClient
from slack.api.models import Event, ReactionAdded, MessageSent


@shared_task
def process_event(self, data):
    slack_api_client = SlackApiClient(settings.SLACK_ACCESS_TOKEN)
    try:
        event_wrapper = Event.from_dict(data)
        event = event_wrapper.get_event()
        print(event)
        team = slack_api_client.get_workspace(data['team_id'])
        print(team)
        if isinstance(event, ReactionAdded):
            user = slack_api_client.get_user(event.user)
            channel = slack_api_client.get_channel(event.item.channel)
            item_user = slack_api_client.get_user(event.item_user)
            added = event.type == 'reaction_added'
            message = slack_api_client.get_message(channel, event.item.ts)

            handle_reaction(
                event.reaction,
                user.name,
                item_user.name,
                message.text,
                added,
                lambda reply: slack_api_client.post_message(channel, reply)
            )
        elif isinstance(event, MessageSent):
            user = slack_api_client.get_user(event.user)
            channel = slack_api_client.get_channel(event.channel)
            if channel.name != 'frisky-logs':
                if event.text.endswith('!log'):
                    slack_api_client.emergency_log(event)
                    event.text = event.text[:-4].rstrip()

                handle_message(
                    channel.name,
                    user.name,
                    event.text,
                    lambda reply: slack_api_client.post_message(channel, reply)
                )
    except Exception as e:
        print(e)
