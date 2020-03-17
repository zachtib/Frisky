from typing import Dict

from emoji.models import EmojiToken
from emoji.service import EmojiApiClient, EmojiService
from frisky.test import FriskyTestCase
from plugins.emoji import EmojiPlugin


class TestEmojiApiClient(EmojiApiClient):
    VALID_NAME = 'emojiland'
    VALID_USER = 'emojimaniac'
    VALID_AUTH = '12345'

    def list_emoji(self, auth: str) -> Dict[str, str]:
        if auth == self.VALID_AUTH:
            return {
                'yes': 'yes-url',
                'nope': 'nope-url'
            }
        return {}


class EmojiServiceTestCase(FriskyTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.service = EmojiService(TestEmojiApiClient())
        for plugin in self.frisky.get_plugins_for_command('emoji'):
            plugin.service = self.service
        EmojiToken.objects.add_token(
            TestEmojiApiClient.VALID_USER,
            TestEmojiApiClient.VALID_NAME,
            TestEmojiApiClient.VALID_AUTH
        )
        EmojiToken.objects.add_token(
            TestEmojiApiClient.VALID_USER,
            EmojiPlugin.LOCAL,
            TestEmojiApiClient.VALID_AUTH
        )

    def test_token_exists(self):
        reply = self.send_message('?emojiauth list', user=TestEmojiApiClient.VALID_USER)
        self.assertEqual('Available tokens: emojiland, local', reply)

    def test_list(self):
        reply = self.send_message('?emoji list emojiland', user=TestEmojiApiClient.VALID_USER)
        self.assertEqual('Emoji include: yes, nope', reply)

    def test_from(self):
        reply = self.send_message('?from emojiland import yes', user=TestEmojiApiClient.VALID_USER)
        self.assertEqual('Summoned :yes:', reply)

    def test_from_without_local(self):
        EmojiToken.objects.filter(name='local').delete()
        reply = self.send_message('?from emojiland import yes', user=TestEmojiApiClient.VALID_USER)
        self.assertEqual("You don't have a saved token for this space.", reply)

    def test_from_without_remote(self):
        EmojiToken.objects.filter(name='emojiland').delete()
        reply = self.send_message('?from emojiland import yes', user=TestEmojiApiClient.VALID_USER)
        self.assertEqual('Error: Could not find a token for emojiland', reply)


class EmojiPluginTestCase(FriskyTestCase):

    def test_adding_a_token(self):
        reply = self.send_message('?emojiauth add foobar 12345', user='testuser')
        self.assertEqual('Added foobar', reply)
        token = EmojiToken.objects.get_token('testuser', 'foobar')
        self.assertIsNotNone(token)
        self.assertEqual('foobar', token.name)
        self.assertEqual('testuser', token.username)
        self.assertEqual('12345', token.token)

    def test_adding_a_local_token(self):
        reply = self.send_message('?emojiauth add 12345', user='testuser')
        self.assertEqual('Added local', reply)
        token = EmojiToken.objects.get_token('testuser', 'local')
        self.assertIsNotNone(token)
        self.assertEqual('local', token.name)
        self.assertEqual('testuser', token.username)
        self.assertEqual('12345', token.token)

    def test_adding_multiple_tokens_with_same_name(self):
        reply = self.send_message('?emojiauth add foobar 12345')
        self.assertEqual('Added foobar', reply)
        reply = self.send_message('?emojiauth add foobar 67890')
        self.assertEqual('Token exists', reply)
