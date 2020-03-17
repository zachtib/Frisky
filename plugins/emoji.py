from typing import Tuple

from emoji.models import EmojiToken
from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse


class EmojiPlugin(FriskyPlugin):
    EMOJI_AUTH = 'emojiauth'

    @classmethod
    def register_commands(cls) -> Tuple:
        return (
            cls.EMOJI_AUTH,
        )

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        if message.command == self.EMOJI_AUTH:
            return self.handle_emoji_auth(message)
        return None

    def handle_emoji_auth(self, message: MessageEvent) -> FriskyResponse:
        if message.args[0] == 'add':
            username = message.username
            token_name = message.args[1]
            token = message.args[2]
            if EmojiToken.objects.add_token(username, token_name, token):
                return f'Added {token_name}'
            return 'Token exists'
        return 'SYNTAX ERROR'
