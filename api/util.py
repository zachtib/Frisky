import logging

import jwt
from django.conf import settings
from django.http import Http404

from api.models import ApiToken


def get_jwt_from_headers(headers):
    auth_header: str = headers.get('Authorization', None)
    if auth_header is None:
        logging.debug('Missing Auth header')
        raise Http404()
    kind, jwt_token = auth_header.split(' ', 1)
    if kind != 'Bearer':
        logging.debug('Auth header is not Bearer')
        raise Http404()
    try:
        decoded_token = jwt.decode(jwt_token, settings.JWT_SECRET, algorithms=['HS256'])
        token = ApiToken.objects.get(uuid=decoded_token.get('uuid', None))
        if token.revoked:
            logging.debug('Token is revoked')
            raise Http404()
        return decoded_token
    except ApiToken.DoesNotExist:
        logging.debug('Token does not exist')
        raise Http404()
    except jwt.exceptions.InvalidSignatureError:
        logging.debug('JWT Invalid Signature')
        raise Http404()
