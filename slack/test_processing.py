import json
from unittest.mock import patch

import responses
from django.test import TestCase
from frisky.models import Workspace, Channel, Member
from slack.api.models import MessageSent
from slack.tasks import process_slack_event

event_payload = '''
{
    "token": "XXYYZZ",
    "team_id": "TXXXXXXXX",
    "api_app_id": "AXXXXXXXXX",
    "event": {
        "type": "message",
        "channel": "C0XXXXXXX",
        "user": "U214XXXXXXX",
        "text": "Live long and prospect.",
        "ts": "1355517523.XXXXXX",
        "event_ts": "1355517523.XXXXXX",
        "channel_type": "channel"
    },
    "type": "event_callback",
    "authed_users": [
            "UXXXXXXX1"
    ],
    "authed_teams": [
            "TXXXXXXXX"
    ],
    "authorizations": [
        {
            "enterprise_id": "E12345",
            "team_id": "T12345",
            "user_id": "U12345",
            "is_bot": false
        }
    ],
    "event_context": "EC12345",
    "event_id": "Ev0XXXXXXX",
    "event_time": 1234567890
}'''.strip()

reaction_event_payload = '''
{
    "token": "XXYYZZ",
    "team_id": "TXXXXXXXX",
    "api_app_id": "AXXXXXXXXX",
    "event": {
        "type": "reaction_added",
        "user": "U0XXXXXXX",
        "reaction": "thumbsup",
        "item_user": "U0XXXXXXX",
        "item": {
            "type": "message",
            "channel": "C0XXXXXXX",
            "ts": "1360782400.XXXXXX"
        },
        "event_ts": "1360782804.XXXXXX"
    },
    "type": "event_callback",
    "authed_users": [
            "UXXXXXXX1"
    ],
    "authed_teams": [
            "TXXXXXXXX"
    ],
    "authorizations": [
        {
            "enterprise_id": "E12345",
            "team_id": "T12345",
            "user_id": "U12345",
            "is_bot": false
        }
    ],
    "event_context": "EC12345",
    "event_id": "EvXXXXXXXX",
    "event_time": 1234567890
}'''.strip()


class SlackEventProcessingTestCase(TestCase):

    def setUp(self) -> None:
        self.workspace = Workspace.objects.create(kind=Workspace.Kind.SLACK, team_id='TXXXXXXXX', name='Testing',
                                                  domain='testing', access_token='xoxo-my_secret_token')
        self.channel = Channel.objects.create(workspace=self.workspace, channel_id='C0XXXXXXX', name='general',
                                              is_channel=True, is_group=False, is_private=False, is_im=False)
        self.user = Member.objects.create(workspace=self.workspace, user_id='U214XXXXXXX', name='testuser',
                                          real_name='Test User')

    @responses.activate
    @patch('slack.tasks.SlackWrapper.handle_message')
    def test_processing_message_event(self, handle_message):
        expected = MessageSent(channel='C0XXXXXXX', user='U214XXXXXXX', text='Live long and prospect.',
                               ts='1355517523.XXXXXX', event_ts='1355517523.XXXXXX', channel_type='channel')
        event = json.loads(event_payload)
        process_slack_event(event)
        handle_message.assert_called_with(expected)
