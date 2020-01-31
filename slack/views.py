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
from slack.api import SlackApi

logger = logging.getLogger(__name__)
api = SlackApi(settings.SLACK_ACCESS_TOKEN)


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
        event = form_data['event']
        workspace = api.get_workspace(form_data['team_id'])
        if event['type'] == 'message':
            """ Example Event:
            "event": {
                "type": "message",
                "channel": "C024BE91L",
                "user": "U2147483697",
                "text": "Live long and prospect.",
                "ts": "1355517523.000005",
                "event_ts": "1355517523.000005",
                "channel_type": "channel"
            }
            """
            user = api.get_user(event['user'])
            channel = api.get_channel(workspace, event['channel'])
            if channel.name != 'frisky-logs':
                if event['text'].endswith('!log'):
                    api.log(event)
                    event['text'] = event['text'][:-4].rstrip()
                handle_message(
                    channel.name,
                    user.name,
                    event['text'],
                    lambda reply: api.post_message(channel, reply)
                )
        elif event['type'] == 'reaction_added' or event['type'] == 'reaction_removed':
            channel = api.get_channel(workspace, event['item']['channel'])
            """
                {
                    "type": "reaction_added",
                    "user": "U024BE7LH",
                    "reaction": "thumbsup",
                    "item_user": "U0G9QF9C6",
                    "item": {
                        "type": "message",
                        "channel": "C0G9QF9GZ",
                        "ts": "1360782400.498405"
                    },
                    "event_ts": "1360782804.083113"
                }
            """
            user = api.get_user(event['user'])  # The person that made the reaction
            item_user = api.get_user(event['item_user'])  # The person that made the comment
            added = event['type'] == 'reaction_added'
            message = api.get_message(event['item']['channel'], event['item']['ts'])
            handle_reaction(
                event['reaction'],
                user.name,
                item_user.name,
                message.text,
                added,
                lambda reply: api.post_message(channel, reply)
            )
