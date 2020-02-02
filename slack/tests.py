from unittest import TestCase

from slack.api.models import Event, ReactionAdded, User


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

    def test_user_deserialization(self):
        user_string = '''{
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
        }'''
        user_obj: User = User.from_json(user_string)

        self.assertEqual(user_obj.profile.display_name_normalized, 'spengler')
