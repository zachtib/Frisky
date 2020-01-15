from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from datetime import time
import hmac


def event(request):
    if request.method == 'POST':
        request_body = request.body()
        timestamp = request.headers['X-Slack-Request-Timestamp']
        slack_signature = request.headers['X-Slack-Signature']
        # if absolute_value(time.time() - timestamp) > 60 * 5:
        #     # The request timestamp is more than five minutes from local time.
        #     # It could be a replay attack, so let's ignore it.
        #     return
        sig_basestring = 'v0:' + timestamp + ':' + request_body
        print(sig_basestring)
        signature = 'v0=' + hmac.digest(settings.SLACK_SIGNING_SECRET, sig_basestring, 'sha256')
        print(signature)
        if signature == slack_signature:
            return HttpResponse(request.POST['challenge'])
    return HttpResponse()
