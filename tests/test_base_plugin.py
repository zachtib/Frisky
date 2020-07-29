from django.test import TestCase

from frisky.events import MessageEvent, ReactionEvent
from frisky.plugin import FriskyPlugin


class BasePluginTestCase(TestCase):

    def setUp(self) -> None:
        self.plugin = FriskyPlugin()

    def test_unhandled_command_returns_none(self):
        message_event = MessageEvent(
            username='testuser',
            channel_name='general',
            text='?hello world'
        )
        response = self.plugin.handle_message(message_event)
        self.assertIsNone(response)

    def test_unhandled_reaction_returns_none(self):
        message_event = MessageEvent(
            username='testuser',
            channel_name='general',
            text='?hello world'
        )
        reaction_event = ReactionEvent(
            emoji='bacon',
            username='testuser2',
            added=True,
            message=message_event
        )
        response = self.plugin.handle_reaction(reaction_event)
        self.assertIsNone(response)
