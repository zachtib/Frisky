from typing import Dict

import requests


# from emoji.service import EmojiApiClient


class SlackEmojiApiClient(object):
    def upload_emoji(self, auth: str, filename: str, name: str) -> bool:
        url = 'https://slack.com/api/emoji.add'

    def list_emoji(self, auth: str) -> Dict[str, str]:
        response = requests.get(f'https://slack.com/api/emoji.list?token={auth}')
        if response.status_code != 200:
            return {}
        json = response.json()
        if not json['ok']:
            return {}
        result = {}

        for name, url in json['emoji'].items():
            if url.startswith('http'):
                result[name] = url
        return result
