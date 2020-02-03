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



    def __api_get_single_message(self, conversation_id, timestamp):
        response = requests.get(f'https://slack.com/api/conversations.history?channel=' +
                                f'{conversation_id}&oldest={timestamp}&latest={timestamp}&inclusive=true&limit=1',
                                headers=self.__headers())
        json = response.json()
        if json['ok']:
            message = json['messages'][0]
            return Message.from_dict(message)
        return None

    def get_message(self, conversation: Conversation, timestamp: str) -> Optional[Message]:
        return cache.get_or_set(Message.create_key(conversation.id, timestamp),
                                lambda: self.__api_get_single_message(conversation.id, timestamp))

    def __api_request(self, path, key=None):
        response = requests.get(f'https://slack.com/api/{path}', headers=self.__headers())
        json = response.json()
        if json['ok']:
            if key:
                return json[key]
            else:
                return json
        else:
            return None

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

    def __api(self, cls, method, key, **kwargs):
        if len(kwargs) > 0:
            method += '?' + '&'.join([f'{key}={value}' for key, value in kwargs.items()])
        return self.__cast(cls, self.__api_request(method, key))

    def __api_user_info(self, user_id) -> Optional[User]:
        return self.__api('users.info', 'user', User, user_id=user_id)
        # return self.__cast(User, self.__api_request(f'users.info?user={user_id}', 'user'))

    def get_user(self, user_id) -> Optional[User]:
        return cache.get_or_set(User.create_key(user_id), lambda: self.__api_user_info(user_id))

    def __api_conversations_info(self, conversation_id) -> Optional[Conversation]:
        """
        https://api.slack.com/methods/conversations.info
        :param conversation_id:
        :return:
        """
        json = self.__api_request(f'conversations.info?channel={conversation_id}')
        if json:
            return Conversation.from_dict(json['channel'])
        return None

    def get_channel(self, channel_id) -> Optional[Conversation]:
        return cache.get_or_set(Conversation.create_key(channel_id), lambda: self.__api_conversations_info(channel_id))

    def __api_team_info(self, team_id) -> Optional[Team]:
        """
        https://slack.com/api/team.info
        :param team_id:
        :return:
        """
        json = self.__api_request(f'team.info?team={team_id}')
        if json:
            return Team.from_dict(json['team'])
        return None

    def get_workspace(self, workspace_id) -> Optional[Team]:
        return cache.get_or_set(Team.create_key(workspace_id), lambda: self.__api_team_info(workspace_id))

    def post_message(self, channel: Conversation, message: str) -> bool:
        requests.post(
            'https://slack.com/api/chat.postMessage',
            json={'channel': channel.id, 'text': message},
            headers=self.__headers()
        )
        return True

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
