from typing import Tuple

from emoji.models import EmojiToken
from emoji.service import EmojiService
from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse


class EmojiPlugin(FriskyPlugin):
    EMOJI_AUTH = 'emojiauth'
    EMOJI = 'emoji'

    def __init__(self) -> None:
        super().__init__()
        from slack.emoji.client import SlackEmojiApiClient
        self.service = EmojiService(SlackEmojiApiClient())

    @classmethod
    def register_commands(cls) -> Tuple:
        return (
            cls.EMOJI_AUTH,
            cls.EMOJI,
        )

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        if message.command == self.EMOJI_AUTH:
            return self.handle_emoji_auth(message)
        elif message.command == self.EMOJI:
            return self.handle_emoji(message)
        return None

    def handle_emoji(self, message: MessageEvent) -> FriskyResponse:
        if message.args[0] == 'list':
            token = EmojiToken.objects.get_token(message.username, message.args[1])
            emoji = self.service.list_emoji(token)
            return 'Emoji include: ' + ', '.join(emoji.keys())
        return None

    def handle_emoji_auth(self, message: MessageEvent) -> FriskyResponse:
        if message.args[0] == 'add':
            username = message.username
            token_name = message.args[1]
            token = message.args[2]
            if EmojiToken.objects.add_token(username, token_name, token):
                return f'Added {token_name}'
            return 'Token exists'
        elif message.args[0] == 'list':
            tokens = EmojiToken.objects.list_tokens(message.username)
            if len(tokens) == 0:
                return 'You have no saved tokens'
            token_names = [token.name for token in tokens]
            return 'Available tokens: ' + ', '.join(token_names)
        return 'SYNTAX ERROR'
