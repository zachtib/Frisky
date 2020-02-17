import os
from dataclasses import dataclass
from typing import Tuple, Optional, Dict

from dataclasses_json import DataClassJsonMixin

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin


@dataclass
class Meme(DataClassJsonMixin):
    # {
    #     "id": "61579",
    #     "name": "One Does Not Simply",
    #     "url": "https://i.imgflip.com/1bij.jpg",
    #     "width": 568,
    #     "height": 335,
    #     "box_count": 2
    # }
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
        return 'meme',

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

    def handle_message(self, message: MessageEvent) -> Optional[str]:
        memes: Dict[str, Meme] = self.cacheify(self.__get_memes)
        meme_name = message.args[0]
        meme_args = message.args[1:]

        result = self.http.post(self.CAPTION_IMAGE_URL, data={
            'template_id': memes[meme_name].id,
            'username': os.environ.get('IMGFLIP_USERNAME', ''),
            'password': os.environ.get('IMGFLIP_PASSWORD', ''),
            'text0': meme_args[0],
            'text1': meme_args[1],
        })
        json = result.json()
        if json['success']:
            return json['data']['url']
        else:
            return json['error_message']

        return None
