import json
import logging

from django.conf import settings
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.util import get_jwt_from_headers
from frisky.events import MessageEvent
from learns.models import Learn


@csrf_exempt
def get_response(request):
    if request.method != 'POST':
        raise Http404()

    api_token = get_jwt_from_headers(request.headers)
    if api_token.get('general', None) != 'true':
        logging.debug('Token was valid, but not for general api')
        raise Http404()
    received_json_data = json.loads(request.body.decode("utf-8"))

    message = received_json_data['message']
    username = received_json_data['username']
    channel = received_json_data['channel']

    if not message.startswith(settings.FRISKY_PREFIX):
        message = f'{settings.FRISKY_PREFIX}{message}'

    from frisky.bot import get_configured_frisky_instance
    frisky = get_configured_frisky_instance()
    responses = frisky.handle_message_synchronously(MessageEvent(
        username=username,
        channel_name=channel,
        text=message
    ))
    return JsonResponse({
        'replies': responses,
    })


def random_learn(request):
    jwt = get_jwt_from_headers(request.headers)
    label = jwt.get('label', None)
    try:
        learn = Learn.objects.random(label)
    except ValueError:
        raise Http404()
    return JsonResponse({
        'result': learn.content,
    })
