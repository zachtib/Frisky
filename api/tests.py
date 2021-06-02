import json
import uuid
from io import StringIO
from typing import Dict

import jwt
from django.conf import settings
from django.core.management import call_command, CommandError

from api.models import ApiToken
from frisky.models import Workspace
from frisky.test import FriskyTestCase


class ApiTestCase(FriskyTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.workspace.kind = Workspace.Kind.SLACK
        self.workspace.save()

    def create_valid_token(self, payload: Dict[str, str], omit_workspace=False) -> str:
        created_token = ApiToken.objects.create(name='Testing Token')
        payload['uuid'] = str(created_token.uuid)
        if not omit_workspace:
            payload['workspace_id'] = str(self.workspace.id)
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256').decode()
        return token

    def create_revoked_token(self, payload: Dict[str, str]) -> str:
        created_token = ApiToken.objects.create(name='Revoked Token', revoked=True)
        payload['uuid'] = str(created_token.uuid)
        payload['workspace_id'] = str(self.workspace.id)
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256').decode()
        return token


class LearnApiTests(ApiTestCase):

    def test_success(self):
        self.send_message('?learn api_test abcdefg')
        token = self.create_valid_token({'label': 'api_test'})

        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['result'], 'abcdefg')

    def test_token_without_workspace_404s(self):
        self.send_message('?learn api_test abcdefg')
        token = self.create_valid_token({'label': 'api_test'}, omit_workspace=True)

        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 404)

    def test_token_with_invalid_workspace_404s(self):
        self.send_message('?learn api_test abcdefg')
        token = self.create_valid_token({'label': 'api_test', 'workspace_id': '123'}, omit_workspace=True)

        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 404)

    def test_token_with_nonexistant_workspace_404s(self):
        self.send_message('?learn api_test abcdefg')
        token = self.create_valid_token({'label': 'api_test', 'workspace_id': str(uuid.uuid4())}, omit_workspace=True)

        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 404)

    def test_revoked_token_404s(self):
        token = self.create_revoked_token({'label': 'api_test'})

        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 404)

    def test_valid_token_not_in_db_404s(self):
        payload = {'label': 'api_test', 'workspace_id': str(self.workspace.id)}
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256').decode()

        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 404)

    def test_invalid_jwt_404s(self):
        token = jwt.encode(
            {
                'label': 'api_test',
                'workspace_id': str(self.workspace.id)
            },
            'my_fake_secret',
            algorithm='HS256').decode()

        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 404)

    def test_no_learns_for_label_404s(self):
        self.send_message('?learn api_test abcdefg')
        token = self.create_valid_token({'label': 'api_test_2'})

        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 404)

    def test_missing_auth_header_404s(self):
        response = self.client.get('/api/random/')

        self.assertEqual(response.status_code, 404)

    def test_non_bearer_auth_header_404s(self):
        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Basic foobar')

        self.assertEqual(response.status_code, 404)


class GeneralApiTests(ApiTestCase):

    def test_general_get_404s(self):
        response = self.client.get('/api/response/')
        self.assertEqual(response.status_code, 404)

    def test_general_without_workspace_404s(self):
        token = self.create_valid_token({'general': 'true'}, omit_workspace=True)

        response = self.client.post(
            '/api/response/',
            data=json.dumps({
                'username': self.get_user('testuser').name,
                'channel': self.get_channel('bot-testing').name,
                'message': '?ping'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )

        self.assertEqual(response.status_code, 404)

    def test_general_with_invalid_workspace_404s(self):
        token = self.create_valid_token({'general': 'true', 'workspace_id': '123'}, omit_workspace=True)

        response = self.client.post(
            '/api/response/',
            data=json.dumps({
                'username': self.get_user('testuser').name,
                'channel': self.get_channel('bot-testing').name,
                'message': '?ping'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )

        self.assertEqual(response.status_code, 404)

    def test_general_with_non_slack_workspace_is_like_nah(self):
        workspace = Workspace.objects.create(kind=Workspace.Kind.NONE, team_id='W00002', name='Testing2',
                                             domain='testing2', access_token='super_secret_token')
        token = self.create_valid_token({'general': 'true', 'workspace_id': str(workspace.id)}, omit_workspace=True)

        response = self.client.post(
            '/api/response/',
            data=json.dumps({
                'username': self.get_user('testuser').name,
                'channel': self.get_channel('bot-testing').name,
                'message': '?ping'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )

        self.assertEqual(response.status_code, 404)

    def test_general_with_nonexistant_workspace_404s(self):
        token = self.create_valid_token({'general': 'true', 'workspace_id': str(uuid.uuid4())}, omit_workspace=True)

        response = self.client.post(
            '/api/response/',
            data=json.dumps({
                'username': self.get_user('testuser').name,
                'channel': self.get_channel('bot-testing').name,
                'message': '?ping'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )

        self.assertEqual(response.status_code, 404)

    def test_general_ping(self):
        token = self.create_valid_token({'general': 'true'})

        response = self.client.post(
            '/api/response/',
            data=json.dumps({
                'username': self.get_user('testuser').name,
                'channel': self.get_channel('bot-testing').name,
                'message': '?ping'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['replies'], ['pong'])

    def test_api_prepends_prefix_ping(self):
        token = self.create_valid_token({'general': 'true'})

        response = self.client.post(
            '/api/response/',
            data=json.dumps({
                'username': self.get_user('testuser').name,
                'channel': self.get_channel('bot-testing').name,
                'message': 'ping'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['replies'], ['pong'])

    def test_learn_token_invalid(self):
        token = self.create_valid_token({'label': 'api_test'})

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


class CommandsTestCase(ApiTestCase):

    def test_issue_jwt_noop(self):
        out = StringIO()
        with self.assertRaises(CommandError, msg='Error: the following arguments are required: --workspace_id'):
            call_command('issuejwt', stdout=out, name='testing')

    def test_issue_jwt_learn(self):
        out = StringIO()
        call_command('issuejwt', stdout=out, name='testing', learn='abcde', workspace_id=str(self.workspace.id))
        _, output = out.getvalue().split(' ')
        decoded_value = jwt.decode(output, key=settings.JWT_SECRET, algorithms=['HS256'])
        token = ApiToken.objects.get(uuid=decoded_value['uuid'])
        self.assertEqual(decoded_value['label'], 'abcde')
        self.assertEqual(token.name, 'testing')

    def test_issue_jwt_general(self):
        out = StringIO()
        call_command('issuejwt', name='testing', general=True, workspace_id=str(self.workspace.id), stdout=out)
        _, output = out.getvalue().split(' ')
        decoded_value = jwt.decode(output, key=settings.JWT_SECRET, algorithms=['HS256'])
        token = ApiToken.objects.get(uuid=decoded_value['uuid'])
        self.assertEqual(decoded_value['general'], 'true')
        self.assertEqual(token.name, 'testing')


class MiscApiTestCase(ApiTestCase):

    def test_api_config(self):
        from api.apps import ApiConfig
        self.assertEqual(ApiConfig.name, 'api')

    def test_api_str(self):
        self.create_valid_token({'label': 'api_test'})
        api_token = ApiToken.objects.get(id=1)
        self.assertEqual('ApiToken: Testing Token', str(api_token))
