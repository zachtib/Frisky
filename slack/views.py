import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from frisky.bot import handle_message, handle_reaction
from frisky.http import FriskyResponse
from slack.api.client import SlackApiClient
from slack.api.models import Event, ReactionAdded, MessageSent

logger = logging.getLogger(__name__)
slack_api_client = SlackApiClient(settings.SLACK_ACCESS_TOKEN)


class SlackEvent(View):
    http_method_names = ('post',)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        form_data = json.loads(request.body.decode())
        if form_data['type'] == 'url_verification':
            if self.verify_slack_request(request):
                return HttpResponse(form_data['challenge'])
            else:
                return HttpResponse(status=404)
        elif 'X-Slack-Retry-Num' in request.headers:
            return HttpResponse(status=200)
        elif form_data['type'] == 'event_callback':
            return FriskyResponse(lambda: self.process_event(form_data))
        else:
            return HttpResponse(status=404)

    @staticmethod
    def verify_slack_request(request):
        slack_request_timestamp = request.headers['X-Slack-Request-Timestamp']
        slack_signature = request.headers['X-Slack-Signature']

        req = str.encode('v0:' + str(slack_request_timestamp) + ':') + request.body
        request_hash = 'v0=' + hmac.new(
            str.encode(settings.SLACK_SIGNING_SECRET),
            req, hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(request_hash, slack_signature):
            return True
        else:
            return False

    def process_event(self, form_data):
        try:
            event_wrapper = Event.from_dict(form_data)
            event = event_wrapper.get_event()
            team = slack_api_client.get_workspace(form_data['team_id'])
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
