import json
from unittest import TestCase
from unittest.mock import MagicMock, PropertyMock

from parameterized import parameterized

from slack.api.models import Event, ReactionAdded, User, Profile, Conversation
from .errors import UnsupportedSlackEventTypeError
from .events import SlackEventParser, MessageSentEvent, MessageChangedEvent, MessageDeletedEvent, MessageRepliedEvent, \
    ReactionAddedEvent, ReactionRemovedEvent
from .processor import SlackEventProcessor, EventProperties
from .test_data import *


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

    def test_dm_deserialization(self):
        convo = Conversation.from_json(dm_json)
        self.assertIsNotNone(convo)
        self.assertIsNone(convo.name)
        self.assertTrue(convo.is_im)


class SlackEventProcessorTestCase(TestCase):

    def setUp(self) -> None:
        self.processor = SlackEventProcessor()

    @parameterized.expand([
        ('reaction_added', None, reaction_added_but_no_item_user_payload),
        ('message', 'message_sent', message_sent_payload),
        ('reaction_added', None, reaction_event_payload),
        ('message', 'message_changed', message_changed_payload),
        ('message', 'message_deleted', message_deleted_payload),
        ('message', 'message_replied', message_replied_payload),
    ])
    def test_parsing_event_properties(self, event_type, event_subtype, payload_str):
        expected = EventProperties(
            event_id='Ev0XXXXXXX',
            team_id='TXXXXXXXX',
            channel_id='C0XXXXXXX',
            user_id='U0XXXXXXX',
            event_type=event_type,
            event_subtype=event_subtype,
        )

        payload = json.loads(payload_str)
        actual = self.processor.parse_event_properties(payload)

        self.assertEqual(expected, actual)

    @parameterized.expand([
        ('message.channel_join', user_joined_payload),
        ('unsupported_event_type', unsupported_payload),
    ])
    def test_parsing_unsupported_events(self, event_type, event_payload):
        payload = json.loads(event_payload)
        with self.assertRaises(UnsupportedSlackEventTypeError) as cm:
            self.processor.parse_event_properties(payload)
            self.assertEqual(event_type, cm.exception.event_type)


class SlackEventParserTestCase(TestCase):
    def setUp(self) -> None:
        self.parser = SlackEventParser()

    @parameterized.expand([
        (message_sent_payload, 'message', 'message_sent', MessageSentEvent),
        (message_changed_payload, 'message', 'message_changed', MessageChangedEvent),
        (message_deleted_payload, 'message', 'message_deleted', MessageDeletedEvent),
        (message_replied_payload, 'message', 'message_replied', MessageRepliedEvent),
        (reaction_event_payload, 'reaction_added', None, ReactionAddedEvent),
        (reaction_removed_payload, 'reaction_removed', None, ReactionRemovedEvent),
    ])
    def test_parsing_message_sent(self, payload_str, event_type, event_subtype, expected_type):
        payload = json.loads(payload_str)
        event_payload = payload['event']

        properties = MagicMock()
        type(properties).event_type = PropertyMock(return_value=event_type)
        type(properties).event_subtype = PropertyMock(return_value=event_subtype)

        event = self.parser.parse_event(properties, event_payload)

        self.assertIsInstance(event, expected_type)
        self.assertEqual(properties.event_id, event.event_id)
        self.assertEqual(properties.team_id, event.team_id)
        self.assertEqual(properties.channel_id, event.channel_id)
        self.assertEqual(properties.user_id, event.user_id)
