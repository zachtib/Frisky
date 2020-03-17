from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional

from django.core.cache import cache

from emoji.models import EmojiToken


@dataclass
class Emoji:
    name: str
    image_url: str


class EmojiApiClient(ABC):

    @abstractmethod
    def list_emoji(self, auth: str) -> Dict[str, str]:
        pass


class EmojiService:
    __client: EmojiApiClient

    def __init__(self, client: EmojiApiClient):
        self.__client = client

    @staticmethod
    def __cache_key(method: str, auth: EmojiToken):
        return f'emoji:{method}:{auth.username}:{auth.name}'

    def list_emoji(self, auth: EmojiToken) -> Dict[str, str]:
        if auth is None:
            return {}
        return cache.get_or_set(
            self.__cache_key('list', auth),
            lambda: self.__client.list_emoji(auth.token)
        )

    def get_emoji(self, auth: EmojiToken, emoji_name) -> Optional[Emoji]:
        # Use the caching call here to just to cut down on total api calls
        emoji = self.list_emoji(auth)
        if emoji and emoji_name in emoji:
            url = emoji[emoji_name]
            return Emoji(emoji_name, url)
        return None

    def upload_emoji(self, auth: EmojiToken, new_emoji_name, new_emoji_url) -> bool:
        return True
