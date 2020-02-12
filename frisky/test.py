from django.test import TestCase

from frisky.bot import Frisky
from frisky.events import MessageEvent, ReactionEvent


class FriskyTestCase(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.frisky = Frisky('frisky')

    def send_message(self, message, user='dummyuser', channel='testing'):
        result = None
        event = MessageEvent(
            username=user,
            channel_name=channel,
            text=message,
            command='',
            args=tuple()
        )

        def callback(response: str) -> bool:
            nonlocal result
            result = response
            return True

        self.frisky.handle_message(event, callback)
        return result

    def send_reaction(self, reaction, from_user, to_user, reacted_message='yolo', channel='testing',
                      reaction_removed=False):
        result = None
        event = ReactionEvent(
            emoji=reaction,
            username=from_user,
            added=not reaction_removed,
            message=MessageEvent(
                username=to_user,
                channel_name=channel,
                text=reacted_message,
                command='',
                args=tuple()
            )
        )

        def callback(response: str) -> bool:
            nonlocal result
            result = response
            return True

        self.frisky.handle_reaction(event, callback)
        return result
