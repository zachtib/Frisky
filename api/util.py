import logging

import jwt
from django.conf import settings
from django.http import Http404

from api.models import ApiToken


def get_jwt_from_headers(headers):
    auth_header: str = headers.get('Authorization', None)
    if auth_header is None:
        logging.debug("Missing Auth header")
        raise Http404()
    kind, jwt_token = auth_header.split(' ', 1)
    if kind != 'Bearer':
        logging.debug("Auth header is not Bearer")
        raise Http404()
    try:
        token = ApiToken.objects.get(jwt=jwt_token)
        if token.revoked:
            logging.debug("Token is revoked")
            raise Http404()
        return jwt.decode(jwt_token, settings.JWT_SECRET, algorithms=['HS256'])
    except ApiToken.DoesNotExist:
        logging.debug("Token does not exist")
    except jwt.exceptions.InvalidSignatureError:
        logging.debug("JWT Invalid Signature")
        raise Http404()
