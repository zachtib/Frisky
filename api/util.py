import jwt
from django.conf import settings
from django.http import Http404


def get_jwt_from_headers(headers):
    auth_header: str = headers.get('Authorization', None)
    if auth_header is None:
        raise Http404()
    kind, jwt_token = auth_header.split(' ', 1)
    if kind != 'Bearer':
        raise Http404()
    try:
        return jwt.decode(jwt_token, settings.JWT_SECRET, algorithms=['HS256'])
    except jwt.exceptions.InvalidSignatureError:
        raise Http404()
