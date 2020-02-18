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

    def __cast(self, cls, obj):
        if obj is None:
            return None
        elif isinstance(obj, dict):
            return cls.from_dict(obj)
        elif isinstance(obj, str):
            return cls.from_json(obj)
        elif isinstance(obj, list):
            return [self.__cast(cls, item) for item in obj]
        else:
            return None

    def get(self, cls, method, key=None, **kwargs):
        if len(kwargs) > 0:
            method += '?' + '&'.join([f'{key}={value}' for key, value in kwargs.items()])

        response = requests.get(f'https://slack.com/api/{method}', headers=self.__headers()).json()

        if not response['ok']:
            return

        if key:
            obj = response[key]
        else:
            obj = response

        return self.__cast(cls, obj)

    def post(self, method: str, json: dict) -> bool:
        response = requests.post(f'https://slack.com/api/{method}', json=json, headers=self.__headers())
        return response.status_code == 200

    def __api_get_single_message(self, conversation_id, timestamp):
        result = self.get(Message,
                          'conversations.history',
                          'messages',
                          channel=conversation_id,
                          oldest=timestamp,
                          latest=timestamp,
                          inclusive='true',
                          limit=1)

        if len(result) == 1:
            return result[0]
        return None

    def get_message(self, conversation: Conversation, timestamp: str) -> Optional[Message]:
        return cache.get_or_set(
            key=Message.create_key(conversation.id, timestamp),
            default=lambda: self.__api_get_single_message(conversation.id, timestamp)
        )

    def get_user(self, user_id) -> Optional[User]:
        return cache.get_or_set(
            key=User.create_key(user_id),
            default=lambda: self.get('users.info', 'user', User, user_id=user_id)
        )

    def get_channel(self, channel_id) -> Optional[Conversation]:
        """
        https://api.slack.com/methods/conversations.info
        :param channel_id: The id of the Channel to locate
        :return: A Conversation object if the channel is found, else None
        """
        return cache.get_or_set(
            key=Conversation.create_key(channel_id),
            default=lambda: self.get(Conversation, 'conversations.info', 'channel', channel=channel_id)
        )

    def get_workspace(self, workspace_id) -> Optional[Team]:
        """
        https://slack.com/api/team.info
        :param workspace_id: The id of the Workspace to locate
        :return: A Team object if the team is found, else None
        """
        return cache.get_or_set(
            key=Team.create_key(workspace_id),
            default=lambda: self.get(Team, 'team.info', 'team', team=workspace_id)
        )

    def post_message(self, channel: Conversation, message: str) -> bool:
        return self.post('chat.postMessage', json={
            'channel': channel.id,
            'text': message,
        })

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
