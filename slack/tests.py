import json
from typing import Callable
from unittest import mock
from unittest.mock import MagicMock, PropertyMock, patch

import responses
from django.core.management import call_command
from django.test import TestCase
from parameterized import parameterized

from frisky.events import ReactionEvent, MessageEvent
from frisky.models import Member, Channel, Workspace
from slack.api.models import Event, User, Profile, Conversation
from .api.models import ReactionAdded, ReactionItem, MessageSent
from .api.tests import URL
from .api.tests import USER_OK
from .errors import UnsupportedSlackEventTypeError
from .events import SlackEventParser, MessageSentEvent, MessageChangedEvent, MessageDeletedEvent, MessageRepliedEvent, \
    ReactionAddedEvent, ReactionRemovedEvent
from .processor import SlackEventProcessor, EventProperties
from .tasks import ingest_from_slack_events_api
from .test_data import *
from .wrapper import SlackWrapper


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


class SlackEventProcessingTestCase(TestCase):

    def setUp(self) -> None:
        self.workspace = Workspace.objects.create(kind=Workspace.Kind.SLACK, team_id='TXXXXXXXX', name='Testing',
                                                  domain='testing', access_token='xoxo-my_secret_token')
        self.channel = Channel.objects.create(workspace=self.workspace, channel_id='C0XXXXXXX', name='general',
                                              is_channel=True, is_group=False, is_private=False, is_im=False)
        self.user = Member.objects.create(workspace=self.workspace, user_id='U214XXXXXXX', name='testuser',
                                          real_name='Test User')
        self.user2 = Member.objects.create(workspace=self.workspace, user_id='U0XXXXXXX', name='otheruser',
                                           real_name='Second User')

    @responses.activate
    @patch('slack.tasks.SlackWrapper.handle_message')
    def test_processing_message_event(self, handle_message):
        expected = MessageSent(channel='C0XXXXXXX', user='U0XXXXXXX', text='Live long and prospect.',
                               ts='1355517523.XXXXXX', event_ts='1355517523.XXXXXX', channel_type='channel')
        event = json.loads(message_sent_payload)
        ingest_from_slack_events_api(event)
        handle_message.assert_called_with(expected)

    @responses.activate
    @patch('slack.tasks.SlackWrapper.handle_reaction')
    def test_processing_reaction_event(self, handle_reaction):
        expected = ReactionAdded(
            type='reaction_added',
            user='U0XXXXXXX',
            reaction='thumbsup',
            item_user='U0XXXXXXX',
            event_ts='1360782804.XXXXXX',
            item=ReactionItem(
                type='message',
                channel='C0XXXXXXX',
                ts='1360782400.XXXXXX'
            ),
        )

        event = json.loads(reaction_event_payload)
        ingest_from_slack_events_api(event)

        handle_reaction.assert_called_once_with(expected)

    @responses.activate
    @patch('slack.tasks.SlackWrapper.handle_message')
    def test_processing_user_joined(self, handle_message):
        event = json.loads(user_joined_payload)
        with self.assertRaises(UnsupportedSlackEventTypeError):
            ingest_from_slack_events_api(event)

        handle_message.assert_not_called()

    @responses.activate
    @patch('slack.tasks.SlackWrapper.handle_message')
    def test_processing_message_changed(self, handle_message):
        event = json.loads(message_changed_payload)
        ingest_from_slack_events_api(event)

        handle_message.assert_not_called()

    @responses.activate
    @patch('slack.tasks.SlackWrapper.handle_message')
    def test_processing_message_deleted(self, handle_message):
        event = json.loads(message_deleted_payload)
        ingest_from_slack_events_api(event)

        handle_message.assert_not_called()

    @responses.activate
    @patch('slack.tasks.SlackWrapper.handle_message')
    def test_processing_message_replied(self, handle_message):
        event = json.loads(message_replied_payload)
        ingest_from_slack_events_api(event)

        handle_message.assert_not_called()

    @responses.activate
    @patch('slack.tasks.SlackWrapper.handle_message')
    def test_processing_no_item_user(self, handle_message):
        event = json.loads(reaction_added_but_no_item_user_payload)
        ingest_from_slack_events_api(event)

        handle_message.assert_not_called()


class EventHandlingTestCase(TestCase):

    def setUp(self) -> None:
        self.workspace = Workspace.objects.create(
            kind=Workspace.Kind.SLACK,
            team_id='T12345',
            name='Testing Slack',
            domain='testing',
            access_token='xoxo-my_secret_token',
        )
        self.channel = Channel.objects.create(workspace=self.workspace, channel_id='123', name='general',
                                              is_channel=True, is_group=False, is_private=False, is_im=False)
        self.user = Member.objects.create(workspace=self.workspace, user_id='W012A3CDE', name='spengler',
                                          real_name='Test User')

        self.wrapper = SlackWrapper(self.workspace, self.channel, self.user)

    @responses.activate
    def test_username_substitution(self):
        responses.add('GET', f'{URL}/users.info?user=W012A3CDE', body=USER_OK)
        result = self.wrapper.replace_usernames('<@W012A3CDE> is a jerk')
        self.assertEqual('spengler is a jerk', result)

    def test_handle_message(self):
        expected = MessageEvent(
            workspace=self.workspace,
            channel=self.channel,
            user=self.user,
            users={self.user.user_id: self.user},
            raw_message='?I like to :poop:',
            username='spengler',
            channel_name='general',
            text='?I like to :poop:',
        )
        result = None

        def mock_handle_message(_, message: MessageEvent, reply_channel: Callable[[str], bool]):
            nonlocal result
            result = message

        patcher = mock.patch(target='frisky.bot.Frisky.handle_message', new=mock_handle_message)

        try:
            patcher.start()
            self.wrapper.handle_message(MessageSent(
                channel='123',
                user='W012A3CDE',
                text='?I like to :poop:',
                ts='123',
                event_ts='123',
                channel_type='channel'
            ))
            self.assertEqual(expected, result)
        finally:
            patcher.stop()

    @responses.activate
    def test_handle_reaction(self):
        expected = ReactionEvent(
            workspace=self.workspace,
            channel=self.channel,
            user=self.user,
            users={self.user.user_id: self.user},
            emoji='poop',
            username='spengler',
            added=True,
            message=MessageEvent(
                workspace=self.workspace,
                channel=self.channel,
                user=self.user,
                users={self.user.user_id: self.user},
                raw_message='I find you punny and would like to smell your nose letter',
                username='spengler',
                channel_name='general',
                text='I find you punny and would like to smell your nose letter',
            )
        )
        result = None

        def mock_handle_reaction(_, reaction: ReactionEvent, reply_channel: Callable[[str], bool]):
            nonlocal result
            result = reaction

        patcher = mock.patch(target='frisky.bot.Frisky.handle_reaction', new=mock_handle_reaction)

        api = f'{URL}/conversations.history?channel=123&oldest=123&latest=123&inclusive=true&limit=1'
        responses.add('GET', api, body=message)
        try:
            patcher.start()
            self.wrapper.handle_reaction(event=ReactionAdded(
                type='reaction_added',
                user='W012A3CDE',
                item=ReactionItem(
                    type='message',
                    channel='123',
                    ts='123'
                ),
                reaction='poop',
                item_user='W012A3CDE',
                event_ts='123'
            ))
            self.assertEqual(expected, result)
        finally:
            patcher.stop()

    @responses.activate
    @patch('frisky.bot.Frisky.handle_reaction')
    def test_reactions_in_a_private_channel(self, handle_reaction):
        api = f'{URL}/conversations.history?channel=C00002&oldest=123&latest=123&inclusive=true&limit=1'
        private_channel = Channel.objects.create(workspace=self.workspace, channel_id='C00002', name='private',
                                                 is_channel=True, is_group=False, is_private=True, is_im=False)
        self.wrapper.channel = private_channel
        responses.add(responses.GET, api, message)

        self.wrapper.handle_reaction(event=ReactionAdded(
            type='reaction_added',
            user='W012A3CDE',
            item=ReactionItem(
                type='message',
                channel='C00002',
                ts='123'
            ),
            reaction='poop',
            item_user='W012A3CDE',
            event_ts='123'
        ))

        handle_reaction.assert_called_once()

    @responses.activate
    @patch('frisky.bot.Frisky.get_plugins_for_reaction')
    def test_that_reactions_in_a_private_channel_blank_message_contents(self, get_plugins_for_reaction):
        api = f'{URL}/conversations.history?channel=C00002&oldest=123&latest=123&inclusive=true&limit=1'
        private_channel = Channel.objects.create(workspace=self.workspace, channel_id='C00002', name='private',
                                                 is_channel=True, is_group=False, is_private=True, is_im=False)
        self.wrapper.channel = private_channel
        responses.add(responses.GET, api, message)
        mock_reply = MagicMock()
        self.wrapper.reply = mock_reply

        mock_plugin = MagicMock()
        get_plugins_for_reaction.return_value = [mock_plugin]
        mock_plugin.handle_reaction = MagicMock()

        self.wrapper.handle_reaction(event=ReactionAdded(
            type='reaction_added',
            user='W012A3CDE',
            item=ReactionItem(
                type='message',
                channel='C00002',
                ts='123'
            ),
            reaction='poop',
            item_user='W012A3CDE',
            event_ts='123'
        ))

        mock_plugin.handle_reaction.assert_called_once()
        actual: ReactionEvent = mock_plugin.handle_reaction.call_args[0][0]
        self.assertIsNone(actual.message.text)
        self.assertIsNone(actual.message.raw_message)


class SlackCliTestCase(TestCase):

    def setUp(self) -> None:
        workspace = Workspace.objects.create(kind=Workspace.Kind.SLACK, team_id='TXXXXXXXX', name='Testing',
                                             domain='testing', access_token='xoxo-my_secret_token')
        Channel.objects.create(workspace=workspace, channel_id='123', name='general',
                               is_channel=True, is_group=False, is_private=False, is_im=False)
        Member.objects.create(workspace=workspace, user_id='W012A3CDE', name='system_user',
                              real_name='Test User')

    @responses.activate
    def test(self):
        responses.add('POST', f'{URL}/chat.postMessage')

        call_command('friskcli', '--workspace', 'testing', '--channel', 'general', 'ping')
        self.assertEqual(b'{"channel": "123", "text": "pong"}', responses.calls[0].request.body)

    @responses.activate
    def test_repeat(self):
        responses.add('POST', f'{URL}/chat.postMessage')
        responses.add('POST', f'{URL}/chat.postMessage')

        call_command('friskcli', '--workspace', 'testing', '--channel', 'general', '--repeat', '2', 'ping')
        self.assertEqual(2, len(responses.calls))
        self.assertEqual(b'{"channel": "123", "text": "pong"}', responses.calls[0].request.body)
        self.assertEqual(b'{"channel": "123", "text": "pong"}', responses.calls[1].request.body)


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
