from django.test import TestCase

from frisky.bot import get_reply_from_plugin


class FriskyTestCase(TestCase):

    def send_message(self, message, channel='testing'):
        return get_reply_from_plugin(message, channel)
