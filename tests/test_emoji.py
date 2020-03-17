from emoji.models import EmojiToken
from frisky.test import FriskyTestCase


class EmojiTestCase(FriskyTestCase):

    def test_adding_a_token(self):
        reply = self.send_message('?emojiauth add foobar 12345', user='testuser')
        self.assertEqual('Added foobar', reply)
        token = EmojiToken.objects.get_token('testuser', 'foobar')
        self.assertIsNotNone(token)
        self.assertEqual('foobar', token.name)
        self.assertEqual('testuser', token.username)
        self.assertEqual('12345', token.token)

    def test_adding_multiple_tokens_with_same_name(self):
        reply = self.send_message('?emojiauth add foobar 12345')
        self.assertEqual('Added foobar', reply)
        reply = self.send_message('?emojiauth add foobar 67890')
        self.assertEqual('Token exists', reply)
