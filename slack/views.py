import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


def verify_slack_request(request):
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


@csrf_exempt
def event(request):
    if verify_slack_request(request):
        form_data = json.loads(request.body.decode())
        if form_data['type'] == 'url_verification':
            return HttpResponse(form_data['challenge'])

        logger.info(form_data)

        return HttpResponse(200)
    else:
        return HttpResponse('Unauthorized', status=401)
