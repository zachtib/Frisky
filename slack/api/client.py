import datetime
from typing import Optional

import requests
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

    def __api_user_info(self, user_id) -> Optional[User]:
        response = requests.get(f'https://slack.com/api/users.info?user={user_id}', headers=self.__headers())
        """
        Example API Response:
            {
                "ok": true,
                "user": {
                    "id": "W012A3CDE",
                    "team_id": "T012AB3C4",
                    "name": "spengler",
                    "deleted": false,
                    "color": "9f69e7",
                    "real_name": "Egon Spengler",
                    "tz": "America/Los_Angeles",
                    "tz_label": "Pacific Daylight Time",
                    "tz_offset": -25200,
                    "profile": {
                        "avatar_hash": "ge3b51ca72de",
                        "status_text": "Print is dead",
                        "status_emoji": ":books:",
                        "real_name": "Egon Spengler",
                        "display_name": "spengler",
                        "real_name_normalized": "Egon Spengler",
                        "display_name_normalized": "spengler",
                        "email": "spengler@ghostbusters.example.com",
                        "image_original": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                        "image_24": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                        "image_32": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                        "image_48": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                        "image_72": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                        "image_192": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                        "image_512": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                        "team": "T012AB3C4"
                    },
                    "is_admin": true,
                    "is_owner": false,
                    "is_primary_owner": false,
                    "is_restricted": false,
                    "is_ultra_restricted": false,
                    "is_bot": false,
                    "updated": 1502138686,
                    "is_app_user": false,
                    "has_2fa": false
                }
            }
        """
        json = response.json()
        if json['ok']:
            user = json['user']
            return User.from_dict(user)
        return None

    def __api_conversations_info(self, conversation_id) -> Optional[Conversation]:
        """
        https://api.slack.com/methods/conversations.info
        :param conversation_id:
        :return:
        """

        response = requests.get(f'https://slack.com/api/conversations.info?channel={conversation_id}',
                                headers=self.__headers())
        json = response.json()
        if json['ok']:
            channel = json['channel']
            return Conversation.from_dict(channel)
        return None

    def __api_team_info(self, team_id) -> Optional[Team]:
        """
        https://slack.com/api/team.info
        :param team_id:
        :return:
        """

        response = requests.get(f'https://slack.com/api/team.info?team={team_id}',
                                headers=self.__headers())
        json = response.json()
        if json['ok']:
            team = json['team']
            return Team.from_dict(team)
        return None

    def __api_get_single_message(self, conversation_id, timestamp):
        response = requests.get(f'https://slack.com/api/conversations.history?channel=' +
                                f'{conversation_id}&oldest={timestamp}&latest={timestamp}&inclusive=true&limit=1',
                                headers=self.__headers())
        json = response.json()
        if json['ok']:
            message = json['messages'][0]
            return Message.from_dict(message)
        return None

    @staticmethod
    def __get_username_from_api_user(user: User) -> str:
        if user.profile is not None:
            name = user.profile.display_name_normalized
            if name is not None and name != '':
                return name
            name = user.profile.real_name_normalized
            if name is not None and name != '':
                return name
        if user.name is not None and user.name != '':
            return user.name
        return 'unknown'

    def get_message(self, conversation: Conversation, timestamp: str) -> Optional[Message]:
        return cache.get_or_set(Message.create_key(conversation.id, timestamp),
                                lambda: self.__api_get_single_message(conversation.id, timestamp))

    def get_user(self, user_id) -> Optional[User]:
        return cache.get_or_set(User.create_key(user_id), lambda: self.__api_user_info(user_id))

    def get_channel(self, channel_id) -> Optional[Conversation]:
        return cache.get_or_set(Conversation.create_key(channel_id), lambda: self.__api_conversations_info(channel_id))

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
            json={'channel': 'frisky-logs', 'text': f'```{message}```'},
            headers=self.__headers()
        )
