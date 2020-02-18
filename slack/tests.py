from unittest import TestCase

from slack.api.models import Event, ReactionAdded, User, Profile, Conversation
from .test_data import user_json, profile_json


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

    def test_user_deserialization_from_null(self):
        with self.assertRaises(AttributeError):
            user = User.from_dict(None)

    def test_user_deserialization_from_empty(self):
        with self.assertRaises(KeyError):
            user = User.from_dict({})

    def test_user_deserialization(self):
        user_obj: User = User.from_json(user_json)
        self.assertEqual('displaynamenormalized', user_obj.profile.display_name_normalized)

    def test_user_short_name(self):
        user_obj: User = User.from_json(user_json)
        self.assertEqual('displaynamenormalized', user_obj.get_short_name())

    def test_user_short_name_with_null_profile(self):
        user_obj: User = User.from_json(user_json)
        user_obj.profile = None
        self.assertEqual('spengler', user_obj.get_short_name())

    def test_user_short_name_with_empty_display_name(self):
        user_obj: User = User.from_json(user_json)
        user_obj.profile.display_name_normalized = ''
        user_obj.profile.display_name = ''
        self.assertEqual('Real Name Normalized', user_obj.get_short_name())

    def test_user_shortname_with_no_values(self):
        user = User(
            id='',
            name='',
            real_name='',
            team_id='',
            profile=Profile(
                real_name='',
                display_name='',
                real_name_normalized='',
                display_name_normalized='',
                team=''
            )
        )
        self.assertEqual(user.get_short_name(), 'unknown')

    def test_cache_key_creation(self):
        self.assertEqual('User:W012A3CDE', User.create_key('W012A3CDE'))

    def test_cache_key_creation_on_instance(self):
        user = User.from_json(user_json)
        self.assertEqual('User:W012A3CDE', user.key())

    def test_cache_key_creation_on_instance_without_id(self):
        profile = Profile.from_json(profile_json)
        self.assertIsNone(profile.key())

    def test_create_with_dict(self):
        convo = Conversation.create({'id': 'asdf', 'name': 'foobar'})
        self.assertEqual('asdf', convo.id)
        self.assertEqual('foobar', convo.name)

    def test_create_with_string(self):
        convo = Conversation.create('{"id": "asdf", "name": "foobar"}')
        self.assertEqual('asdf', convo.id)
        self.assertEqual('foobar', convo.name)

    def test_create_with_list(self):
        data = [{'id': 'asdf', 'name': 'foobar'}, '{"id": "asdf2", "name": "foobar2"}']
        convos = Conversation.create(data)
        self.assertIsInstance(convos, list)
        self.assertEqual('asdf', convos[0].id)
        self.assertEqual('foobar', convos[0].name)
        self.assertEqual('asdf2', convos[1].id)
        self.assertEqual('foobar2', convos[1].name)

    def test_create_with_none(self):
        convo = Conversation.create(None)
        self.assertIsNone(convo)
