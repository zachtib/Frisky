from typing import Tuple, Optional

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin, PluginRepositoryMixin
from frisky.responses import FriskyResponse, FriskyError
from learns.models import Learn
from memes.models import MemeAlias


class MemeLearnPlugin(FriskyPlugin, PluginRepositoryMixin):
    _help_text = 'Usage: `?memelearn <THING TO MEME>`'

    @classmethod
    def help_text(cls) -> Optional[str]:
        return cls._help_text

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'memelearn',

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        if len(message.args) != 1 or message.args[0] == 'help':
            return self._help_text
        meme_id = MemeAlias.objects.get_id_for_alias(message.args[0])
        if meme_id == -1:
            return FriskyError('NO SUCH MEME')
        try:
            meme_message: str = Learn.objects.random(message.args[0]).content
        except ValueError:
            return 'NO SUCH LEARN'
        return self.get_plugin_for_command('meme').handle_message(MessageEvent(
            username=message.username,
            channel_name=message.channel_name,
            text='',
            command='meme',
            args=[message.args[0], '', meme_message],
        ))
