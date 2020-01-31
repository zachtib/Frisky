import datetime

import requests

from slack.models import Workspace, Channel, User, Message


class SlackApiClient(object):
    __access_token: str
    __cache_timeout: datetime.timedelta
    __user_cache: dict
    __channel_cache: dict

    def __init__(self, access_token, cache_timeout=86400):
        self.__access_token = access_token
        self.__cache_timeout = datetime.timedelta(seconds=cache_timeout)
        self.__user_cache = dict()
        self.__channel_cache = dict()

    def __headers(self):
        return {'Authorization': f'Bearer {self.__access_token}'}

    def __api_user_info(self, user_id):
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
            return user
        return None

    @staticmethod
    def __get_username_from_api_user(user) -> str:
        profile = user.get('profile', None)
        if profile is not None:
            name = profile.get('display_name_normalized', None)
            if name is not None and name != '':
                return name
            name = profile.get('real_name_normalized', None)
            if name is not None and name != '':
                return name
        name = user.get('name', None)
        if name is not None and name != '':
            return name
        return 'unknown'

    def get_message(self, channel: Channel, timestamp: str) -> Message:
        """
        {
            "ok": true,
            "messages": [
                {
                    "type": "message",
                    "user": "U012AB3CDE",
                    "text": "I find you punny and would like to smell your nose letter",
                    "ts": "1512085950.000216"
                },
                {
                    "type": "message",
                    "user": "U061F7AUR",
                    "text": "What, you want to smell my shoes better?",
                    "ts": "1512104434.000490"
                }
            ],
            "has_more": true,
            "pin_count": 0,
            "response_metadata": {
                "next_cursor": "bmV4dF90czoxNTEyMDg1ODYxMDAwNTQz"
            }
        }
        :param channel:
        :param timestamp:
        :return:
        """
        response = requests.get(f'https://slack.com/api/conversations.history?channel=' +
                                f'{channel.slack_id}&oldest={timestamp}&latest={timestamp}&inclusive=true&limit=1',
                                headers=self.__headers())
        json = response.json()
        if json['ok']:
            message = json['messages'][0]
            return Message(
                channel=channel,
                user=self.get_user(message['user']),
                text=message['text']
            )

    def get_channel(self, workspace: Workspace, channel_id) -> Channel:
        """
        {
            "ok": true,
            "channel": {
                "id": "C012AB3CD",
                "name": "general",
                "is_channel": true,
                "is_group": false,
                "is_im": false,
                "created": 1449252889,
                "creator": "W012A3BCD",
                "is_archived": false,
                "is_general": true,
                "unlinked": 0,
                "name_normalized": "general",
                "is_read_only": false,
                "is_shared": false,
                "parent_conversation": null,
                "is_ext_shared": false,
                "is_org_shared": false,
                "pending_shared": [],
                "is_pending_ext_shared": false,
                "is_member": true,
                "is_private": false,
                "is_mpim": false,
                "last_read": "1502126650.228446",
                "topic": {
                    "value": "For public discussion of generalities",
                    "creator": "W012A3BCD",
                    "last_set": 1449709364
                },
                "purpose": {
                    "value": "This part of the workspace is for fun. Make fun here.",
                    "creator": "W012A3BCD",
                    "last_set": 1449709364
                },
                "previous_names": [
                    "specifics",
                    "abstractions",
                    "etc"
                ],
                "locale": "en-US"
            }
        }
        :param workspace:
        :param channel_id:
        :return:
        """
        response = requests.get(f'https://slack.com/api/conversations.info?channel={channel_id}',
                                headers=self.__headers())
        json = response.json()
        if json['ok']:
            channel = json['channel']
            return Channel(
                workspace=workspace,
                name=channel['name'],
                slack_id=channel['id']
            )

    def get_workspace(self, team_id) -> Workspace:
        obj, created = Workspace.objects.get_or_create(slack_id=team_id, defaults={'name': ''})
        return obj

    def get_user(self, user_id) -> User:
        try:
            result = User.objects.get(slack_id=user_id)
            elapsed = datetime.datetime.now() - result.last_update
            if elapsed > self.__cache_timeout:
                user_info = self.__api_user_info(result.slack_id)
                result.name = self.__get_username_from_api_user(user_info)
                result.save()
        except User.DoesNotExist:
            user_info = self.__api_user_info(user_id)
            result = User.objects.create(
                name=self.__get_username_from_api_user(user_info),
                workspace=self.get_workspace(user_info['team_id'])
            )
        return result

    def post_message(self, channel: Channel, message: str) -> bool:
        requests.post(
            'https://slack.com/api/chat.postMessage',
            json={'channel': channel.slack_id, 'text': message},
            headers=self.__headers()
        )
        return True

    def log(self, message):
        requests.post(
            'https://slack.com/api/chat.postMessage',
            json={'channel': 'frisky-logs', 'text': f'```{message}```'},
            headers=self.__headers()
        )
