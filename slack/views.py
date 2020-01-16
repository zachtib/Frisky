import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .webhooks import post_message

logger = logging.getLogger(__name__)


def verify_slack_request(request):
    if settings.DEBUG:
        logger.info(f'Headers: {request.headers}')
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


def handle_message(event):
    text = event['text']
    logger.info(f'Message is: {text}')
    if text[0] == '?':
        channel = event['channel']
        if text == '?ping':
            post_message(channel, 'pong', settings.SLACK_ACCESS_TOKEN)
            return HttpResponse(status=200)
        else:
            post_message(channel, 'Oi, I dunno what ya want', settings.SLACK_ACCESS_TOKEN)
            return HttpResponse(status=200)
    else:
        return HttpResponse(status=200)


@csrf_exempt
def handle_event(request):
    if settings.DEBUG:
        logger.debug(f'request={request}')
        logger.debug(f'request.body={request.body})')

    if request.method == 'POST':
        if verify_slack_request(request):
            form_data = json.loads(request.body.decode())
            if form_data['type'] == 'url_verification':
                return HttpResponse(form_data['challenge'])
            elif form_data['type'] == 'event_callback':
                # Handle an event
                event = form_data['event']
                logger.info(f'Handling {event}')
                if event['type'] == 'message':
                    return handle_message(event)
                else:
                    pass
            logger.info(form_data)

            return HttpResponse(200)
        else:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=404)
