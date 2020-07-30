import json

import jwt
from django.conf import settings
from django.test import TestCase

from frisky.test import FriskyTestCase


class LearnApiTests(FriskyTestCase):

    def test_success(self):
        self.send_message('?learn api_test abcdefg')
        token = jwt.encode({'label': 'api_test'}, settings.JWT_SECRET, algorithm='HS256').decode()

        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['result'], 'abcdefg')

    def test_no_learns_for_label_404s(self):
        self.send_message('?learn api_test abcdefg')
        token = jwt.encode({'label': 'api_test_2'}, settings.JWT_SECRET, algorithm='HS256').decode()

        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(response.status_code, 404)

    def test_missing_auth_header_404s(self):
        response = self.client.get('/api/random/')

        self.assertEqual(response.status_code, 404)

    def test_non_bearer_auth_header_404s(self):
        response = self.client.get('/api/random/', HTTP_AUTHORIZATION=f'Basic foobar')

        self.assertEqual(response.status_code, 404)


class ApiConfigTestCase(TestCase):

    def test_api_config(self):
        from api.apps import ApiConfig
        self.assertEqual(ApiConfig.name, 'api')
