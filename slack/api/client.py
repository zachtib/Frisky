import datetime
from typing import Optional

import requests
from django.conf import settings
from django.core.cache import cache

from slack.api.models import User, Conversation, Team, Message


class SlackApiClient(object):
    __access_token: str
    __cache_timeout: datetime.timedelta

    def __init__(self, access_token, cache_timeout=86400):
        self.__access_token = access_token
        self.__cache_timeout = datetime.timedelta(seconds=cache_timeout)

    def __headers(self):
        return {'Authorization': f'Bearer {self.__access_token}'}

    def __get(self, cls, method: str, key: str, **kwargs) -> Optional[object]:
        if len(kwargs) > 0:
            method += '?' + '&'.join([f'{key}={value}' for key, value in kwargs.items()])

        response = requests.get(f'https://slack.com/api/{method}', headers=self.__headers()).json()
        print(response)

        if not response['ok']:
            self.emergency_log(response)
            return None

        return cls.create(response[key])

    def __post(self, method: str, **kwargs) -> bool:
        response = requests.post(f'https://slack.com/api/{method}', json=kwargs, headers=self.__headers())
        return response.status_code == 200

    def __api_get_single_message(self, conversation_id, timestamp):
        result = self.__get(Message,
                            'conversations.history',
                            'messages',
                            channel=conversation_id,
                            oldest=timestamp,
                            latest=timestamp,
                            inclusive='true',
                            limit=1)

        if result is not None and isinstance(result, list) and len(result) == 1:
            return result[0]
        return None

    def get_message(self, conversation: Conversation, timestamp: str) -> Optional[Message]:
        return cache.get_or_set(
            key=Message.create_key(conversation.id, timestamp),
            default=lambda: self.__api_get_single_message(conversation.id, timestamp)
        )

    def get_user(self, user_id) -> Optional[User]:
        print(f'Getting user {user_id}')
        return cache.get_or_set(
            key=User.create_key(user_id),
            default=lambda: self.__get(User, 'users.info', 'user', user=user_id)
        )

    def get_channel(self, channel_id) -> Optional[Conversation]:
        """
        https://api.slack.com/methods/conversations.info
        :param channel_id: The id of the Channel to locate
        :return: A Conversation object if the channel is found, else None
        """
        return cache.get_or_set(
            key=Conversation.create_key(channel_id),
            default=lambda: self.__get(Conversation, 'conversations.info', 'channel', channel=channel_id)
        )

    def get_workspace(self, workspace_id) -> Optional[Team]:
        """
        https://slack.com/api/team.info
        :param workspace_id: The id of the Workspace to locate
        :return: A Team object if the team is found, else None
        """
        return cache.get_or_set(
            key=Team.create_key(workspace_id),
            default=lambda: self.__get(Team, 'team.info', 'team', team=workspace_id)
        )

    def post_image(self, channel: Conversation, image_url: str, alt_text='Image') -> bool:
        if alt_text is None or alt_text == '':
            alt_text = 'Image'
        return self.__post('chat.postMessage', channel=channel.id, blocks=[{
            'type': 'image',
            'image_url': image_url,
            'alt_text': alt_text,
        }])

    def post_message(self, channel: Conversation, message: str) -> bool:
        return self.__post('chat.postMessage', channel=channel.id, text=message)

    def emergency_log(self, message):
        """
        DO NOT USE!
        :param message:
        :return:
        """
        requests.post(
            'https://slack.com/api/chat.postMessage',
            json={'channel': settings.FRISKY_LOGGING_CHANNEL, 'text': f'```{message}```'},
            headers=self.__headers()
        )
