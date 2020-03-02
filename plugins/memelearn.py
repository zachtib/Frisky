from typing import Tuple

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse
from learns.queries import get_random_learn
from memes.models import MemeAlias
from plugins.meme import MemePlugin


class MemeLearnPlugin(FriskyPlugin):

    def __init__(self) -> None:
        super().__init__()
        self.meme_plugin = MemePlugin()

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'memelearn',

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        if len(message.args) != 1 or message.args[0] == 'help':
            return 'Usage: `?memelearn <THING TO MEME>`'
        meme_id = MemeAlias.objects.get_id_for_alias()
        if meme_id == -1:
            return 'NO SUCH MEME'
        try:
            meme_message: str = get_random_learn(message.args[0]).content
        except ValueError:
            return 'NO SUCH LEARN'
        return self.meme_plugin.handle_message(MessageEvent(
            username=message.username,
            channel_name=message.channel_name,
            text=f'?meme {meme_id} "" "{message}"',
            command='meme',
            args=('', meme_message),
        ))
