import json
from unittest import TestCase

import pytest
import responses

from slack.api.models import Event, ReactionAdded, User, Profile, Conversation
from .api.tests import URL
from .tasks import process_event
from .test_data import *


@pytest.mark.parametrize('event_json', [bot_event_json, no_user_reaction_json, message_deleted_event])
def test_ignore_msg(event_json):
    # Test will fail because emergency log will be called and response mock setup with 0 calls
    with responses.RequestsMock() as rm:
        assert process_event(json.loads(event_json)) is None


def test_rubbish_handled():
    with responses.RequestsMock() as rm:
        rm.add('POST', f'{URL}/chat.postMessage')
        assert process_event(json.loads(complete_and_utter_rubbish)) is None


class SlackApiModelsTestCase(TestCase):

    def test_event_deserialization(self):
        event: Event = Event.from_json(reg_event_json)

        self.assertEqual(event.token, "z26uFbvR1xHJEdHE1OQiO6t8")
        self.assertEqual(event.event_id, "Ev9UQ52YNA")

    def test_event_item_deserialization(self):
        event_wrapper: Event = Event.from_json(item_event_json)

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


