from django.test import TestCase

from frisky.bot import get_reply_from_plugin, get_reply_for_reaction


class FriskyTestCase(TestCase):

    def send_message(self, message, channel='testing'):
        return get_reply_from_plugin(message, 'noone', channel)

    def send_reaction(self, reaction, from_user, to_user, reaction_removed=False):
        return get_reply_for_reaction(reaction, from_user, to_user, not reaction_removed)
