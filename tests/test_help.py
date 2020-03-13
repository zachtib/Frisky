from frisky.test import FriskyTestCase


class HelpTestCase(FriskyTestCase):

    def test_help(self):
        reply = self.send_message('?help')
        self.assertTrue(reply.startswith('Available plugins'))

    def test_help_help(self):
        reply = self.send_message('?help help')
        self.assertEqual(reply, 'Usage: `?help` or `?help <plugin_name>`')

    def test_help_asdf(self):
        reply = self.send_message('?help asdf')
        self.assertEqual(reply, 'No such plugin: `asdf`, try `?help` to list installed plugins')
