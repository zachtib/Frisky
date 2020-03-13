from unittest import TestCase

from frisky.bot import Frisky
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
