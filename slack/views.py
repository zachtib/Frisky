import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .bot import handle_message
from .webhooks import slog

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


@csrf_exempt
def handle_event(request) -> HttpResponse:
    if settings.DEBUG:
        slog(f'Headers: {request.headers}')
        slog(f'Body: {request.body}')

    if request.method == 'POST':
        form_data = json.loads(request.body.decode())
        if form_data['type'] == 'url_verification':
            if verify_slack_request(request):
                return HttpResponse(form_data['challenge'])
            else:
                return HttpResponse(status=401)

        if form_data['type'] == 'event_callback':
            event_id = form_data['event_id']
            if event_id in event_cache:
                logger.debug(f'Skipping previously handled event: {event_id}')
                return HttpResponse(status=200)
            # Handle an event
            event = form_data['event']
            event_cache.add(event_id)
            if event['type'] == 'message' and event['channel'] != 'frisky-logs':
                handle_message(event)
        else:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=404)
    return HttpResponse(200)
