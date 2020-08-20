import json
import logging

from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.util import get_jwt_from_headers, handle_generic_frisky_request
from learns.queries import get_random_learn_for_label


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

    responses = handle_generic_frisky_request(message, username, channel)

    return JsonResponse(responses)


def bespoke(request):
    jwt = get_jwt_from_headers(request.headers)

    message = jwt.get('command')
    username = jwt.get('username', '')
    channel = jwt.get('channel', '')

    responses = handle_generic_frisky_request(message, username, channel)
    return JsonResponse(responses)


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
