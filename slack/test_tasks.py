import uuid
from typing import Callable
from unittest import mock
from unittest.mock import MagicMock

import responses
from django.core.management import call_command
from django.test import TestCase

from frisky.events import ReactionEvent, MessageEvent
from frisky.models import Workspace, Member, Channel
from .api.models import ReactionAdded, ReactionItem, MessageSent
from .api.tests import URL
from .api.tests import USER_OK
from .tasks import SlackWrapper

conversation = """
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
}
"""

message = """
{
    "ok": true,
    "latest": "1512085950.000216",
    "messages": [
        {
            "type": "message",
            "user": "U012AB3CDE",
            "text": "I find you punny and would like to smell your nose letter",
            "ts": "1512085950.000216"
        }
    ],
    "has_more": true,
    "pin_count": 0,
    "response_metadata": {
        "next_cursor": "bmV4dF90czoxNTEyMzU2NTI2MDAwMTMw"
    }
}
"""


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
