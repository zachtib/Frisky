import responses

from unittest import TestCase

from frisky.bot import Frisky
from frisky.events import MessageEvent
from frisky.http import PostProcessingResponse
from frisky.util import quotesplit
from frisky.plugin import FriskyApiPlugin


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
    MESSAGE = MessageEvent('user', 'test', '?api')

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

    def test_non_200_response(self):
        plugin = FriskyApiPluginTestCase.JsonTestPlugin()
        with responses.RequestsMock() as rm:
            rm.add('GET', 'https://example.com/api/', status=500)
            actual = plugin.handle_message(FriskyApiPluginTestCase.MESSAGE)
            self.assertIsNone(actual)

    def test_json_parsing(self):
        plugin = FriskyApiPluginTestCase.JsonTestPlugin()
        with responses.RequestsMock() as rm:
            rm.add('GET', 'https://example.com/api/', body=self.JSON_RESPONSE)
            actual = plugin.handle_message(FriskyApiPluginTestCase.MESSAGE)
            self.assertEqual(actual, 'Hello, Json')

    def test_text_parsing(self):
        plugin = FriskyApiPluginTestCase.TextTestPlugin()
        with responses.RequestsMock() as rm:
            rm.add('GET', 'https://example.com/api/', body=self.TEXT_RESPONSE)
            actual = plugin.handle_message(FriskyApiPluginTestCase.MESSAGE)
            self.assertEqual(actual, 'Hello, World')


class HttpTestCase(TestCase):

    def test_post_processing_response_executes_block(self):
        result = False

        def block():
            nonlocal result
            result = True

        response = PostProcessingResponse(block=block)
        response.close()
        self.assertTrue(result)
