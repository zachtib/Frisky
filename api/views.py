import json

from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.util import get_jwt_from_headers
from frisky.events import MessageEvent
from learns.queries import get_random_learn_for_label


@csrf_exempt
def get_response(request):
    if request.method != 'POST':
        raise Http404()

    get_jwt_from_headers(request.headers)
    received_json_data = json.loads(request.body.decode("utf-8"))

    message = received_json_data['message']
    username = received_json_data['username']
    channel = received_json_data['channel']

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
        learn = get_random_learn_for_label(label)
    except ValueError:
        raise Http404()
    return JsonResponse({
        'result': learn.content,
    })
