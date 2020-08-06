import json
from io import StringIO

import jwt
from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from api.models import ApiToken
from frisky.test import FriskyTestCase


def get_valid_token(payload):
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256').decode()
    ApiToken.objects.create(jwt=token, name='Testing Token')
    return token


def get_revoked_token(payload):
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256').decode()
    ApiToken.objects.create(jwt=token, name='Testing Token', revoked=True)
    return token


class LearnApiTests(FriskyTestCase):

    def test_success(self):
        self.send_message('?learn api_test abcdefg')
        token = get_valid_token({'label': 'api_test'})

        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['result'], 'abcdefg')

    def test_revoked_token_404s(self):
        token = get_revoked_token({'label': 'api_test'})

        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 404)

    def test_valid_token_not_in_db_404s(self):
        payload = {'label': 'api_test'}
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256').decode()

        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 404)

    def test_invalid_jwt_404s(self):
        token = jwt.encode({'label': 'api_test'}, 'my_fake_secret', algorithm='HS256').decode()

        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 404)

    def test_no_learns_for_label_404s(self):
        self.send_message('?learn api_test abcdefg')
        token = get_valid_token({'label': 'api_test_2'})

        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 404)

    def test_missing_auth_header_404s(self):
        response = self.client.get('/api/random/')

        self.assertEqual(response.status_code, 404)

    def test_non_bearer_auth_header_404s(self):
        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Basic foobar')

        self.assertEqual(response.status_code, 404)


class GeneralApiTests(FriskyTestCase):

    def test_general_get_404s(self):
        response = self.client.get('/api/response/')
        self.assertEqual(response.status_code, 404)

    def test_general_ping(self):
        token = get_valid_token({'general': 'true'})

        response = self.client.post(
            '/api/response/',
            data=json.dumps({
                'username': 'testuser',
                'channel': 'bot-testing',
                'message': '?ping'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['replies'], ['pong'])

    def test_api_prepends_prefix_ping(self):
        token = get_valid_token({'general': 'true'})

        response = self.client.post(
            '/api/response/',
            data=json.dumps({
                'username': 'testuser',
                'channel': 'bot-testing',
                'message': 'ping'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['replies'], ['pong'])

    def test_learn_token_invalid(self):
        token = get_valid_token({'label': 'api_test'})

        response = self.client.post(
            '/api/response/',
            data=json.dumps({
                'username': 'testuser',
                'channel': 'bot-testing',
                'message': '?ping'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )

        self.assertEqual(response.status_code, 404)


class CommandsTestCase(TestCase):

    def test_issue_jwt_noop(self):
        args = []
        opts = {
            'name': 'testing',
        }
        out = StringIO()
        call_command('issuejwt', *args, **opts, stdout=out)
        self.assertEqual('', out.getvalue())

    def test_issue_jwt_learn(self):
        out = StringIO()
        call_command('issuejwt', name='testing', learn='abcde', stdout=out)
        token = ApiToken.objects.get(id=1)
        decoded_value = jwt.decode(token.jwt, key=settings.JWT_SECRET, algorithms=['HS256'])
        self.assertEqual(decoded_value['label'], 'abcde')

    def test_issue_jwt_general(self):
        out = StringIO()
        call_command('issuejwt', name='testing', general=True, stdout=out)
        token = ApiToken.objects.get(id=1)
        decoded_value = jwt.decode(token.jwt, key=settings.JWT_SECRET, algorithms=['HS256'])
        self.assertEqual(decoded_value['general'], 'true')


class MiscApiTestCase(TestCase):

    def test_api_config(self):
        from api.apps import ApiConfig
        self.assertEqual(ApiConfig.name, 'api')

    def test_api_str(self):
        token = get_valid_token({'label': 'api_test'})
        api_token = ApiToken.objects.get(jwt=token)
        self.assertEqual('ApiToken: Testing Token', str(api_token))
