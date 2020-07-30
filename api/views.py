import jwt
from django.conf import settings
from django.http import Http404, JsonResponse

from learns.queries import get_random_learn_for_label


def random_learn(request):
    auth_header: str = request.headers.get('Authorization', None)
    if auth_header is None:
        raise Http404()
    kind, jwt_token = auth_header.split(' ', 1)
    if kind != 'Bearer':
        raise Http404()
    decoded_payload = jwt.decode(jwt_token, settings.JWT_SECRET, algorithms=['HS256'])
    label = decoded_payload.get('label', None)
    try:
        learn = get_random_learn_for_label(label)
    except ValueError:
        raise Http404()
    return JsonResponse({
        'result': learn.content,
    })
