import logging

import jwt
from django.conf import settings
from django.http import Http404

from api.models import ApiToken
from frisky.bot import get_configured_frisky_instance
from frisky.events import MessageEvent


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


def handle_generic_frisky_request(message, username='', channel=''):
    if message is None:
        raise Http404()
    if not message.startswith(settings.FRISKY_PREFIX):
        message = f'{settings.FRISKY_PREFIX}{message}'
    frisky = get_configured_frisky_instance()
    responses = frisky.handle_message_synchronously(MessageEvent(
        username=username,
        channel_name=channel,
        text=message
    ))
    return {
        'replies': responses,
    }
