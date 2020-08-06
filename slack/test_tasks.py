from typing import Callable
from unittest import mock

import responses
from django.core.management import call_command
from django.test import TestCase

from frisky.events import ReactionEvent, MessageEvent
from .api.models import ReactionAdded, ReactionItem, MessageSent
from .api.tests import URL
from .api.tests import USER_OK
from .tasks import sanitize_message_text, handle_reaction_event, handle_message_event

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

    def test_username_substitution(self):
        with responses.RequestsMock() as rm:
            rm.add('GET', f'{URL}/users.info?user=W012A3CDE', body=USER_OK)
            result = sanitize_message_text('<@W012A3CDE> is a jerk')
            self.assertEqual('spengler is a jerk', result)

    def test_handle_message(self):
        expected = MessageEvent(
            username='spengler',
            channel_name='general',
            text='?I like to :poop:',
        )
        result = None

        def mock_handle_message(_, message: MessageEvent, reply_channel: Callable[[str], bool]):
            nonlocal result
            result = message

        patcher = mock.patch(target='frisky.bot.Frisky.handle_message', new=mock_handle_message)

        with responses.RequestsMock() as rm:
            rm.add('GET', f'{URL}/users.info?user=W012A3CDE', body=USER_OK)
            rm.add('GET', f'{URL}/conversations.info?channel=123', body=conversation)

            try:
                patcher.start()
                handle_message_event(MessageSent(
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

    def test_handle_reaction(self):
        expected = ReactionEvent(
            emoji='poop',
            username='spengler',
            added=True,
            message=MessageEvent(
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

        with responses.RequestsMock() as rm:
            rm.add('GET', f'{URL}/users.info?user=W012A3CDE', body=USER_OK)
            rm.add('GET', f'{URL}/conversations.info?channel=123', body=conversation)
            api = f'{URL}/conversations.history?channel=C012AB3CD&oldest=123&latest=123&inclusive=true&limit=1'
            rm.add('GET', api, body=message)
            try:
                patcher.start()
                handle_reaction_event(event=ReactionAdded(
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

    def test(self):
        result = None

        def mock_handle_message(_, message: MessageEvent, reply_channel: Callable[[str], bool]):
            nonlocal result
            result = message

        patcher = mock.patch(target='frisky.bot.Frisky.handle_message', new=mock_handle_message)
        with responses.RequestsMock() as rm:
            rm.add('POST', f'{URL}/chat.postMessage')

            try:
                patcher.start()
                call_command('friskcli', 'ping')
                self.assertEqual(b'{"channel": null, "text": "pong"}', rm.calls[0].request.body)
                self.assertIsNone(result)
            finally:
                patcher.stop()
