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
            "type": "name_of_event",
            "event_ts": "1234567890.123456",
            "user": "UXXXXXXX1"
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
    "event_id": "Ev08MFMKH6",
    "event_time": 1234567890
}'''.strip()


class SlackViewsTestCase(TestCase):
    EVENTS_URL = '/slack/events/'

    @responses.activate
    @patch('slack.tasks.process_slack_event.delay')
    def test_payload_with_celery_correctly_enqueues_task(self, process_slack_event):
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
    def test_payload_without_celery(self):
        with self.settings(ENABLE_CELERY_QUEUE=False):
            response = self.client.post(
                self.EVENTS_URL,
                data=event_payload,
                content_type='application/json',
            )
        self.assertEqual(200, response.status_code)
