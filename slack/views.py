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
    if settings.DEBUG:
        return True
    slack_request_timestamp = request.headers['X-Slack-Request-Timestamp']
    slack_signature = request.headers['X-Slack-Signature']

    form_data = json.loads(request.body.decode())
    request_body = '&'.join([f'{key}={value}' for key, value in form_data.items()])

    basestring = f"v0:{slack_request_timestamp}:{request_body}".encode('utf-8')
    slack_signing_secret = bytes(settings.SLACK_SIGNING_SECRET, 'utf-8')
    signature = 'v0=' + hmac.new(slack_signing_secret, basestring, hashlib.sha256).hexdigest()

    if hmac.compare_digest(signature, slack_signature):
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
        if verify_slack_request(request):
            form_data = json.loads(request.body.decode())
            if form_data['type'] == 'url_verification':
                return HttpResponse(form_data['challenge'])
            elif form_data['type'] == 'event_callback':
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
