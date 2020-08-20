import json
from io import StringIO

import jwt
from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from api.models import ApiToken
from frisky.test import FriskyTestCase


def get_valid_token(payload):
    created_token = ApiToken.objects.create(name='Testing Token')
    payload['uuid'] = str(created_token.uuid)
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256').decode()
    return token


def get_revoked_token(payload):
    created_token = ApiToken.objects.create(name='Revoked Token', revoked=True)
    payload['uuid'] = str(created_token.uuid)
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256').decode()
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


class BespokeApiTests(FriskyTestCase):

    def test_bespoke_ping(self):
        token = get_valid_token({'command': 'ping'})
        response = self.client.get('/api/bespoke/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['replies'], ['pong'])

    def test_bespoke_with_missing_message_404s(self):
        token = get_valid_token({})
        response = self.client.get('/api/bespoke/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 404)

    def test_bespoke_with_missing_auth_404s(self):
        response = self.client.get('/api/bespoke/')

        self.assertEqual(response.status_code, 404)


class CommandsTestCase(TestCase):

    def test_issue_jwt_noop(self):
        out = StringIO()
        call_command('issuejwt', stdout=out, name='testing')
        self.assertEqual('', out.getvalue())

    def test_issue_jwt_learn(self):
        out = StringIO()
        call_command('issuejwt', stdout=out, name='testing', learn='abcde')
        _, output = out.getvalue().split(' ')
        decoded_value = jwt.decode(output, key=settings.JWT_SECRET, algorithms=['HS256'])
        token = ApiToken.objects.get(uuid=decoded_value['uuid'])
        self.assertEqual(decoded_value['label'], 'abcde')
        self.assertEqual(token.name, 'testing')

    def test_issue_jwt_general(self):
        out = StringIO()
        call_command('issuejwt', name='testing', general=True, stdout=out)
        _, output = out.getvalue().split(' ')
        decoded_value = jwt.decode(output, key=settings.JWT_SECRET, algorithms=['HS256'])
        token = ApiToken.objects.get(uuid=decoded_value['uuid'])
        self.assertEqual(decoded_value['general'], 'true')
        self.assertEqual(token.name, 'testing')

    def test_issue_jwt_bespoke(self):
        out = StringIO()
        call_command('issuejwt', name='testing', command='ping', username='testuser', channel='testchannel', stdout=out)
        _, output = out.getvalue().split(' ')
        decoded_value = jwt.decode(output, key=settings.JWT_SECRET, algorithms=['HS256'])
        token = ApiToken.objects.get(uuid=decoded_value['uuid'])
        self.assertEqual(decoded_value['command'], 'ping')
        self.assertEqual(decoded_value['username'], 'testuser')
        self.assertEqual(decoded_value['channel'], 'testchannel')
        self.assertEqual(token.name, 'testing')


class MiscApiTestCase(TestCase):

    def test_api_config(self):
        from api.apps import ApiConfig
        self.assertEqual(ApiConfig.name, 'api')

    def test_api_str(self):
        get_valid_token({'label': 'api_test'})
        api_token = ApiToken.objects.get(id=1)
        self.assertEqual('ApiToken: Testing Token', str(api_token))
