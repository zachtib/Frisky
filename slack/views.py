import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


def verify_slack_request(request):
    if request.method == 'POST':
        form_data = json.loads(request.body.decode())
        request_body = '&'.join([f'{key}={value}' for key, value in form_data.items()])
        logger.info(request_body)
        slack_request_timestamp = request.headers['X-Slack-Request-Timestamp']
        print(slack_request_timestamp)
        slack_signature = request.headers['X-Slack-Signature']
        print(slack_signature)

        basestring = f"v0:{slack_request_timestamp}:{request_body}".encode('utf-8')
        print(basestring)
        slack_signing_secret = bytes(settings.SLACK_SIGNING_SECRET, 'utf-8')

        signature = 'v0=' + hmac.new(slack_signing_secret, basestring, hashlib.sha256).hexdigest()
        print(signature)

        if hmac.compare_digest(signature, slack_signature):
            return True
        else:
            return False


@csrf_exempt
def event(request):
    form_data = json.loads(request.body.decode())
    logger.info(f'form_data: {form_data}')
    if verify_slack_request(request):
        return HttpResponse(form_data['challenge'])
    return HttpResponse(form_data['challenge'])
