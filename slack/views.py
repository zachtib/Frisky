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
from slack.webhooks import post_message, conversations_info, log_to_slack, user_info, get_message

logger = logging.getLogger(__name__)


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
            event = form_data['event']
            return FriskyResponse(lambda: self.process_event(event))
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

    @staticmethod
    def get_user_name(user):
        profile = user.get('profile', None)
        if profile is not None:
            name = profile.get('display_name_normalized', None)
            if name is not None and name != '':
                return name
            name = profile.get('real_name_normalized', None)
            if name is not None and name != '':
                return name
        name = user.get('name', None)
        if name is not None and name != '':
            return name
        return 'unknown'

    def process_event(self, event):
        if event['type'] == 'message':
            user = user_info(event['user'])
            user_name = self.get_user_name(user)
            channel = conversations_info(event['channel'])
            if channel['name'] != 'frisky-logs':
                if event['text'].endswith('!log'):
                    log_to_slack(str(event))
                    event['text'] = event['text'][:-4].rstrip()
                handle_message(channel['name'], user_name, event['text'],
                               lambda reply: post_message(channel['id'], reply))
        elif event['type'] == 'reaction_added' or event['type'] == 'reaction_removed':
            channel = conversations_info(event['item']['channel'])
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
            user = user_info(event['user'])  # The person that made the reaction
            item_user = user_info(event['item_user'])  # The person that made the comment
            added = event['type'] == 'reaction_added'
            message = get_message(event['item']['channel'], event['item']['ts'])
            user_name = self.get_user_name(user)
            item_user_name = self.get_user_name(item_user)
            handle_reaction(event['reaction'], user_name, item_user_name, message['text'], added,
                            lambda reply: post_message(channel['id'], reply))
