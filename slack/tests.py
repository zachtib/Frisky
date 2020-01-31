from unittest import TestCase

from slack.api.models import Event, ReactionAdded


class SlackApiModelsTestCase(TestCase):

    def test_event_deserialization(self):
        json_string = '''{
                "token": "z26uFbvR1xHJEdHE1OQiO6t8",
                "team_id": "T061EG9RZ",
                "api_app_id": "A0FFV41KK",
                "event": {
                        "type": "reaction_added",
                        "user": "U061F1EUR",
                        "item": {
                                "type": "message",
                                "channel": "C061EG9SL",
                                "ts": "1464196127.000002"
                        },
                        "reaction": "slightly_smiling_face",
                        "item_user": "U0M4RL1NY",
                        "event_ts": "1465244570.336841"
                },
                "type": "event_callback",
                "authed_users": [
                        "U061F7AUR"
                ],
                "event_id": "Ev9UQ52YNA",
                "event_time": 1234567890
        }'''
        event: Event = Event.from_json(json_string)

        self.assertEqual(event.token, "z26uFbvR1xHJEdHE1OQiO6t8")
        self.assertEqual(event.event_id, "Ev9UQ52YNA")

    def test_event_item_deserialization(self):
        json_string = '''{
                "token": "z26uFbvR1xHJEdHE1OQiO6t8",
                "team_id": "T061EG9RZ",
                "api_app_id": "A0FFV41KK",
                "event": {
                        "type": "reaction_added",
                        "user": "U061F1EUR",
                        "item": {
                                "type": "message",
                                "channel": "C061EG9SL",
                                "ts": "1464196127.000002"
                        },
                        "reaction": "slightly_smiling_face",
                        "item_user": "U0M4RL1NY",
                        "event_ts": "1465244570.336841"
                },
                "type": "event_callback",
                "authed_users": [
                        "U061F7AUR"
                ],
                "event_id": "Ev9UQ52YNA",
                "event_time": 1234567890
        }'''
        event_wrapper: Event = Event.from_json(json_string)

        event = event_wrapper.get_event()
        self.assertTrue(isinstance(event, ReactionAdded))
