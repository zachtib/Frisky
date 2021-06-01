import hashlib
import hmac
import json

from django.conf import settings
from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from frisky.friskyhttp import PostProcessingResponse
from slack.tasks import process_slack_event


class SlackEvent(View):
    http_method_names = ('post',)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request_body = request.body.decode()
        form_data = json.loads(request_body)
        if form_data['type'] == 'url_verification':
            if self.verify_slack_request(request):
                return HttpResponse(form_data['challenge'])
            else:
                return HttpResponse(status=404)
        elif 'X-Slack-Retry-Num' in request.headers:
            return HttpResponse(status=200)
        elif form_data['type'] == 'event_callback':
            if settings.ENABLE_CELERY_QUEUE:
                process_slack_event.delay(form_data)
                return HttpResponse(status=200)
            else:
                return PostProcessingResponse(
                    status=200,
                    block=lambda: process_slack_event(form_data)
                )
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
