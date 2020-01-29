import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from frisky.bot import handle_message, handle_reaction
from frisky.http import FriskyResponse
from slack.webhooks import post_message, conversations_info, log_to_slack, user_info, get_message

logger = logging.getLogger(__name__)


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


event_cache = set()


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
        

def process_event(event):
    if event['type'] == 'message':
        channel = conversations_info(event['channel'])
        if channel['name'] != 'frisky-logs':
            if event['text'].endswith('!log'):
                log_to_slack(str(event))
                event['text'] = event['text'][:-4].rstrip()
            handle_message(channel['name'], '', event['text'], lambda reply: post_message(channel['id'], reply))
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
        user_name = get_user_name(user)
        item_user_name = get_user_name(item_user)
        handle_reaction(event['reaction'], user_name, item_user_name, message['text'], added,
                        lambda reply: post_message(channel['id'], reply))


@csrf_exempt
def handle_event(request) -> HttpResponse:
    if request.method == 'POST':
        form_data = json.loads(request.body.decode())
        if form_data['type'] == 'url_verification':
            if verify_slack_request(request):
                return HttpResponse(form_data['challenge'])
            else:
                return HttpResponse(status=404)
        if 'X-Slack-Retry-Num' in request.headers:
            return HttpResponse(status=200)
        if form_data['type'] == 'event_callback':
            event_id = form_data['event_id']
            if event_id in event_cache:
                logger.debug(f'Skipping previously handled event: {event_id}')
                return HttpResponse(status=200)
            # Handle an event
            event = form_data['event']
            event_cache.add(event_id)
            return FriskyResponse(lambda: process_event(event))
        else:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=404)
