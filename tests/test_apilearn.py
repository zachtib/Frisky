import responses

from apilearns.models import ApiLearn
from frisky.test import FriskyTestCase


class ApiLearnTestCase(FriskyTestCase):
    TEXT_RESPONSE = 'Hello, World'

    JSON_RESPONSE = '''
    {
        "hello": {
            "world": "Hello, Json"
        }
    }
    '''

    JSON_RESPONSE_WITH_ARRAY = '''
    {
        "hello": [
            {
                "world": "Hello, Array"
            }
        ]
    }
    '''

    JSON_RESPONSE_CONTAINING_NULL = '''
    {
        "hello": null
    }
    '''

    URL = 'https://example.com/api/'

    def test_creation(self):
        actual = self.send_message(f'?learnapi apitest {self.URL}')
        self.assertEqual(actual, 'OK, learned apitest')
        learn = ApiLearn.objects.get(id=1)
        self.assertEqual('apitest', learn.label)
        self.assertEqual(self.URL, learn.url)
        self.assertIsNone(learn.element)

    def test_creation_slack_url_formatting(self):
        actual = self.send_message(f'?learnapi apitest <{self.URL}>')
        self.assertEqual(actual, 'OK, learned apitest')
        learn = ApiLearn.objects.get(id=1)
        self.assertEqual('apitest', learn.label)
        self.assertEqual(self.URL, learn.url)
        self.assertIsNone(learn.element)

    def test_creation_with_json(self):
        actual = self.send_message(f'?learnapi apitest {self.URL} hello.world')
        self.assertEqual(actual, 'OK, learned apitest')
        learn = ApiLearn.objects.get(id=1)
        self.assertEqual('apitest', learn.label)
        self.assertEqual(self.URL, learn.url)
        self.assertEqual('hello.world', learn.element)

    def test_usage(self):
        ApiLearn.objects.create(label='apitest', url=self.URL)
        with responses.RequestsMock() as rm:
            rm.add('GET', self.URL, body=self.TEXT_RESPONSE)
            actual = self.send_message('?apitest')
            self.assertEqual('Hello, World', actual)

    def test_usage_with_json(self):
        ApiLearn.objects.create(label='apitest', url=self.URL, element='hello.world')
        with responses.RequestsMock() as rm:
            rm.add('GET', self.URL, body=self.JSON_RESPONSE)
            actual = self.send_message('?apitest')
            self.assertEqual('Hello, Json', actual)

    def test_usage_with_json_containing_array(self):
        ApiLearn.objects.create(label='apitest', url=self.URL, element='hello.0.world')
        with responses.RequestsMock() as rm:
            rm.add('GET', self.URL, body=self.JSON_RESPONSE_WITH_ARRAY)
            actual = self.send_message('?apitest')
            self.assertEqual('Hello, Array', actual)

    def test_json_null_termination(self):
        ApiLearn.objects.create(label='apitest', url=self.URL, element='hello.world')
        with responses.RequestsMock() as rm:
            rm.add('GET', self.URL, body=self.JSON_RESPONSE_CONTAINING_NULL)
            actual = self.send_message('?apitest')
            self.assertIsNone(actual)

    def test_delete_doesnotexist(self):
        actual = self.send_message('?unlearnapi apitest')
        self.assertIsNone(actual)

    def test_delete(self):
        ApiLearn.objects.create(label='apitest', url=self.URL)
        actual = self.send_message('?unlearnapi apitest')
        self.assertEqual(actual, 'OK, unlearned apitest')

    def test_commandlearn_invalid_arg_count(self):
        self.assertIsNone(self.send_message('?learnapi foobar'))

    def test_commandunlearn_invalid_arg_count(self):
        self.assertIsNone(self.send_message('?unlearnapi'))

    def test_usage_with_parameters(self):
        ApiLearn.objects.create(label='paramtest', url='http://foo.bar/${1}/')
        with responses.RequestsMock() as rm:
            rm.add('GET', 'http://foo.bar/test/', body=self.TEXT_RESPONSE)
            actual = self.send_message('?paramtest test')
            self.assertEqual('Hello, World', actual)

    def test_headers_for_text(self):
        ApiLearn.objects.create(label='apitest', url=self.URL)
        with responses.RequestsMock() as rm:
            rm.add('GET', self.URL, body=self.TEXT_RESPONSE)
            self.send_message('?apitest')
            request = rm.calls[0].request
            accept_header = request.headers['Accept']
            self.assertEqual('text/plain', accept_header)

    def test_headers_for_json(self):
        ApiLearn.objects.create(label='apitest', url=self.URL, element='hello.world')
        with responses.RequestsMock() as rm:
            rm.add('GET', self.URL, body=self.JSON_RESPONSE)
            self.send_message('?apitest')
            request = rm.calls[0].request
            accept_header = request.headers['Accept']
            self.assertEqual('application/json', accept_header)

    def test_nonexistant_api(self):
        self.assertIsNone(self.send_message('?get_api xyzzy'))
