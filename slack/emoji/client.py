from typing import Dict

from emoji.service import EmojiApiClient


class SlackEmojiApiClient(EmojiApiClient):
    def list_emoji(self, auth: str) -> Dict[str, str]:
        return {}
