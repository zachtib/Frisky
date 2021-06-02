import json
from unittest.mock import patch

from django.test import TestCase

import responses

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

slack_team_ok = '''
{
    "ok": true,
    "team": {
        "id": "TXXXXXXXX",
        "name": "My Team",
        "domain": "example",
        "email_domain": "example.com",
        "icon": {
            "image_34": "https://...",
            "image_44": "https://...",
            "image_68": "https://...",
            "image_88": "https://...",
            "image_102": "https://...",
            "image_132": "https://...",
            "image_default": true
        },
        "enterprise_id": "E1234A12AB",
        "enterprise_name": "Umbrella Corporation"
    }
}
'''.strip()

channel_ok = '''
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
}'''.strip()
user_ok_response = '''
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
            "real_name": "Real Name",
            "display_name": "displayname",
            "real_name_normalized": "Real Name Normalized",
            "display_name_normalized": "displaynamenormalized",
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
}'''.strip()


class SlackViewsTestCase(TestCase):
    EVENTS_URL = '/slack/events/'

    @responses.activate
    @patch('slack.views.ingest_from_slack_events_api.delay')
    def test_message_payload_with_celery_correctly_enqueues_task(self, process_slack_event):
        payload_dict = json.loads(event_payload)
        with self.settings(ENABLE_CELERY_QUEUE=True):
            response = self.client.post(
                self.EVENTS_URL,
                data=event_payload,
                content_type='application/json',
            )
        self.assertEqual(200, response.status_code)
        process_slack_event.assert_called_once_with(payload_dict)

    @responses.activate
    @patch('slack.views.ingest_from_slack_events_api')
    def test_message_payload_without_celery(self, process_slack_event):
        payload_dict = json.loads(event_payload)
        with self.settings(ENABLE_CELERY_QUEUE=False):
            response = self.client.post(
                self.EVENTS_URL,
                data=event_payload,
                content_type='application/json',
            )
        self.assertEqual(200, response.status_code)
        process_slack_event.assert_called_once_with(payload_dict)

    @responses.activate
    @patch('slack.views.ingest_from_slack_events_api.delay')
    def test_reaction_payload_with_celery_correctly_enqueues_task(self, process_slack_event):
        payload_dict = json.loads(reaction_event_payload)
        with self.settings(ENABLE_CELERY_QUEUE=True):
            response = self.client.post(
                self.EVENTS_URL,
                data=reaction_event_payload,
                content_type='application/json',
            )
        self.assertEqual(200, response.status_code)
        process_slack_event.assert_called_once_with(payload_dict)

    @responses.activate
    @patch('slack.views.ingest_from_slack_events_api')
    def test_reaction_payload_without_celery(self, process_slack_event):
        payload_dict = json.loads(reaction_event_payload)
        with self.settings(ENABLE_CELERY_QUEUE=False):
            response = self.client.post(
                self.EVENTS_URL,
                data=reaction_event_payload,
                content_type='application/json',
            )
        self.assertEqual(200, response.status_code)
        process_slack_event.assert_called_once_with(payload_dict)

    @responses.activate
    def test_message_payload_without_celery_calls_into_processor(self):
        responses.add(responses.GET, 'https://slack.com/api/team.info?team=TXXXXXXXX', slack_team_ok)
        responses.add(responses.GET, 'https://slack.com/api/conversations.info?channel=C0XXXXXXX', channel_ok)
        responses.add(responses.GET, 'https://slack.com/api/users.info?user=U214XXXXXXX', user_ok_response)
        with self.settings(ENABLE_CELERY_QUEUE=False, SLACK_ACCESS_TOKEN='my-token'):
            response = self.client.post(
                self.EVENTS_URL,
                data=event_payload,
                content_type='application/json',
            )
        self.assertEqual(200, response.status_code)
