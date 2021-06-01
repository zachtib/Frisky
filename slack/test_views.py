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


class SlackViewsTestCase(TestCase):
    EVENTS_URL = '/slack/events/'

    @responses.activate
    @patch('slack.views.process_slack_event.delay')
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
    @patch('slack.views.process_slack_event')
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
    @patch('slack.views.process_slack_event.delay')
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
    @patch('slack.views.process_slack_event')
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
