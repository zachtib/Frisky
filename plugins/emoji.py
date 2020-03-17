from typing import Tuple

from emoji.models import EmojiToken
from emoji.service import EmojiService
from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse


class EmojiPlugin(FriskyPlugin):
    EMOJI_AUTH = 'emojiauth'
    EMOJI = 'emoji'
    FROM = 'from'
    LOCAL = 'local'

    FROM_USAGE = 'Usage: `from <workspace> import :<emoji>: [as :<new_emoji>:]`'

    def __init__(self) -> None:
        super().__init__()
        from slack.emoji.client import SlackEmojiApiClient
        self.service = EmojiService(SlackEmojiApiClient())

    @classmethod
    def register_commands(cls) -> Tuple:
        return (
            cls.EMOJI_AUTH,
            cls.EMOJI,
            cls.FROM,
        )

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        if message.command == self.EMOJI_AUTH:
            return self.handle_emoji_auth(message)
        elif message.command == self.EMOJI:
            return self.handle_emoji(message)
        elif message.command == self.FROM:
            return self.handle_from(message)
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
            if len(message.args) == 3:
                token_name = message.args[1]
                token = message.args[2]
            else:
                token_name = self.LOCAL
                token = message.args[1]
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

    @staticmethod
    def emoji_name(name: str) -> str:
        return name.strip(':')

    def handle_from(self, message: MessageEvent) -> FriskyResponse:
        #      0  1      2  3  4
        # from $1 import $2
        # from $1 import $2 as $3
        nargs = len(message.args)
        if nargs != 3 and nargs != 5:
            return self.FROM_USAGE
        remote_token = EmojiToken.objects.get_token(message.username, message.args[0])
        if remote_token is None:
            return f'Error: Could not find a token for {message.args[0]}'
        if message.args[1] != 'import':
            return self.FROM_USAGE
        emoji_name = self.emoji_name(message.args[2])
        if nargs == 5 and message.args[3] != 'as':
            return self.FROM_USAGE
        new_emoji_name = self.emoji_name(message.args[4]) if nargs == 5 else emoji_name
        local_token = EmojiToken.objects.get_token(message.username, self.LOCAL)
        if local_token is None:
            return 'You don\'t have a saved token for this space.'
        emoji = self.service.get_emoji(remote_token, emoji_name)
        if emoji is None:
            return f'Could not find `:{emoji_name}:` in {remote_token.name}'

        if self.service.upload_emoji(local_token, new_emoji_name, emoji.image_url):
            return f'Summoned :{new_emoji_name}:'
        else:
            return f'Error uploading emoji to this space'
