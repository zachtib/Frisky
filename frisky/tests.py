from unittest import TestCase
from unittest.mock import MagicMock

import pytest
import responses

from frisky.bot import Frisky
from frisky.events import MessageEvent
from frisky.friskyhttp import PostProcessingResponse
from frisky.plugin import FriskyApiPlugin
from frisky.util import quotesplit


class FriskyBotTestCase(TestCase):

    def setUp(self) -> None:
        self.frisky = Frisky('frisky', plugin_modules=None)

    def test_simple_message_parsing(self):
        result = self.frisky.parse_message_string('?help')
        expected = ('help', [])
        self.assertTupleEqual(result, expected)

    def test_parsing_nothing(self):
        result = self.frisky.parse_message_string('')
        expected = ('', [])
        self.assertTupleEqual(result, expected)

    def test_parsing_just_questionmark(self):
        result = self.frisky.parse_message_string('?')
        expected = ('', [])
        self.assertTupleEqual(result, expected)

    def test_parsing_unrelated_message(self):
        result = self.frisky.parse_message_string('I like cats')
        expected = ('', [])
        self.assertTupleEqual(result, expected)


class FriskyUtilTestCase(TestCase):

    def test_basic_quotesplit(self):
        result = quotesplit('foo bar')
        expected = ['foo', 'bar']
        self.assertEqual(result, expected)

    def test_quotesplit_with_quotes(self):
        result = quotesplit('foo bar "foo bar"')
        expected = ['foo', 'bar', 'foo bar']
        self.assertEqual(result, expected)

    def test_quotesplit_empty(self):
        result = quotesplit('foo ""')
        expected = ['foo', '']
        self.assertEqual(result, expected)

    def test_quotesplit_nested(self):
        result = quotesplit('foo "bar \'blah\'"')
        expected = ['foo', "bar 'blah'"]
        self.assertEqual(result, expected)

    def test_quotesplit_errors_with_dupe_chars(self):
        with self.assertRaises(ValueError):
            quotesplit("", separators=('a', 'b'), groupers=('b', 'c'))


class FriskyApiPluginTestCase(TestCase):
    MESSAGE = MessageEvent(
        workspace=MagicMock(),
        channel=MagicMock(),
        user=MagicMock(),
        users={},
        raw_message='?api',
        username='user',
        channel_name='test',
        text='?api'
    )

    TEXT_RESPONSE = 'Hello, World'

    JSON_RESPONSE = '''
    {
        "hello": {
            "world": "Hello, Json"
        }
    }
    '''

    class JsonTestPlugin(FriskyApiPlugin):
        url = 'https://example.com/api/'
        json_property = 'hello.world'

    class TextTestPlugin(FriskyApiPlugin):
        url = 'https://example.com/api/'

    @responses.activate
    def test_non_200_response(self):
        plugin = FriskyApiPluginTestCase.JsonTestPlugin()
        responses.add('GET', 'https://example.com/api/', status=500)
        actual = plugin.handle_message(FriskyApiPluginTestCase.MESSAGE)
        self.assertIsNone(actual)

    @responses.activate
    def test_json_parsing(self):
        plugin = FriskyApiPluginTestCase.JsonTestPlugin()
        responses.add('GET', 'https://example.com/api/', body=self.JSON_RESPONSE)
        actual = plugin.handle_message(FriskyApiPluginTestCase.MESSAGE)
        self.assertEqual(actual, 'Hello, Json')

    @responses.activate
    def test_text_parsing(self):
        plugin = FriskyApiPluginTestCase.TextTestPlugin()
        responses.add('GET', 'https://example.com/api/', body=self.TEXT_RESPONSE)
        actual = plugin.handle_message(FriskyApiPluginTestCase.MESSAGE)
        self.assertEqual(actual, 'Hello, World')


@pytest.mark.django_db
class HttpTestCase(TestCase):

    def test_post_processing_response_executes_block(self):
        result = False

        def block():
            nonlocal result
            result = True

        response = PostProcessingResponse(block=block)
        response.close()
        self.assertTrue(result)
