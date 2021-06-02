import json
from unittest.mock import patch

import responses
from django.test import TestCase

from frisky.models import Workspace, Channel, Member
from slack.api.models import MessageSent, ReactionAdded, ReactionItem
from slack.errors import UnsupportedSlackEventTypeError
from slack.tasks import ingest_from_slack_events_api
from .test_data import *


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
        expected = MessageSent(channel='C0XXXXXXX', user='U214XXXXXXX', text='Live long and prospect.',
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
