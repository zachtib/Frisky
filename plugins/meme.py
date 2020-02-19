import os
from dataclasses import dataclass
from typing import Tuple, Optional, Dict

from dataclasses_json import DataClassJsonMixin

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from memes.models import MemeAlias


@dataclass
class Meme(DataClassJsonMixin):
    id: str
    name: str
    url: str
    width: int
    height: int
    box_count: 2


class MemePlugin(FriskyPlugin):
    GET_MEMES_URL = 'https://api.imgflip.com/get_memes'
    CAPTION_IMAGE_URL = 'https://api.imgflip.com/caption_image'

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'meme', 'memealias'

    def __get_memes(self) -> Optional[Dict[str, Meme]]:
        response = self.http.get(self.GET_MEMES_URL)
        json = response.json()
        if json['success']:
            meme_list = json['data']['memes']
            result = {}
            for item in meme_list:
                meme = Meme.from_dict(item)
                result[meme.name] = meme
            return result
        return None

    def __memes(self) -> Optional[Dict[str, Meme]]:
        return self.cacheify(self.__get_memes)

    def __handle_memealias(self, message: MessageEvent) -> Optional[str]:
        if len(message.args) == 2:
            try:
                meme_id = int(message.args[1])
            except ValueError:
                return 'Usage: `?memealias <alias> <id>`'
            if MemeAlias.objects.create_alias(message.args[0], meme_id):
                return f'Ok, added {message.args[0]}'
            return 'Error: alias already exists'
        if len(message.args) == 1 and message.args[0] == 'list':
            return ', '.join(MemeAlias.objects.get_all_aliases())
        return 'Usage: `?memealias <alias> <id>` or `?memealias list`'

    def __handle_meme(self, message: MessageEvent) -> Optional[str]:
        if len(message.args) == 0:
            memes: Dict[str, Meme] = self.__memes()
            if memes is None:
                return 'NO MEMES'
            return ', '.join([f'"{name}"' for name in memes.keys()])

        if len(message.args) != 3:
            return 'Usage: `?meme <meme_id> <text0> <text1>`'

        meme_name = message.args[0]
        meme_args = message.args[1:]

        meme_id = MemeAlias.objects.get_id_for_alias(meme_name)

        if meme_id == -1:
            memes: Dict[str, Meme] = self.__memes()
            if memes is None:
                return 'NO MEMES'
            if meme_name in memes.keys():
                meme_id = memes[meme_name].id

        if meme_id == -1:
            return 'NO SUCH MEME'

        result = self.http.post(self.CAPTION_IMAGE_URL, data={
            'template_id': meme_id,
            'username': os.environ.get('IMGFLIP_USERNAME', ''),
            'password': os.environ.get('IMGFLIP_PASSWORD', ''),
            'text0': meme_args[0],
            'text1': meme_args[1],
        })

        json = result.json()
        if json['success']:
            return json['data']['url']
        return json['error_message']

    def handle_message(self, message: MessageEvent) -> Optional[str]:
        if message.command == 'memealias':
            return self.__handle_memealias(message)
        return self.__handle_meme(message)
