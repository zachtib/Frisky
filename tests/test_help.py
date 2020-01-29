from frisky.test import FriskyTestCase


class HelpTestCase(FriskyTestCase):

    def test_help(self):
        reply = self.send_message('?help')
        self.assertTrue(reply.startswith('Available plugins'))
        self.assertTrue('help' in reply)

    def test_help_help(self):
        reply = self.send_message('?help help')
        self.assertEqual(reply, 'Usage: `?help` or `?help <plugin_name>`')
