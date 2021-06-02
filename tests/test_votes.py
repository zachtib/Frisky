from datetime import date
from unittest.mock import patch

from frisky.test import FriskyTestCase
from votes.models import Vote


class VoteTestCase(FriskyTestCase):

    def test_upvote_user_has_one_vote(self):
        self.send_reaction('upvote', 'user_a', 'user_b')
        record = Vote.objects.get_record('user_b')
        self.assertEqual(record.votes, 1)

    def test_downvote_user_has_neg_one_vote(self):
        self.send_reaction('downvote', 'user_a', 'user_b')
        record = Vote.objects.get_record('user_b')
        self.assertEqual(record.votes, -1)

    def test_vote_query(self):
        reply = self.send_message('?votes user_b')
        self.assertTrue(reply.startswith('user_b has 0'))
        record = Vote.objects.get_record('user_b')
        self.assertEqual(record.votes, 0)

    def test_upvote_via_cmd(self):
        self.send_message('?upvote stonks')
        record = Vote.objects.get_record('stonks')
        self.assertEqual(record.votes, 1)

    def test_upvote_via_alias(self):
        self.send_message('?++ stonks')
        self.send_message('?++ stonks')
        self.send_message('?++ stonks')
        record = Vote.objects.get_record('stonks')
        self.assertEqual(record.votes, 3)

    def test_downvote_via_cmd(self):
        self.send_message('?downvote stonks')
        record = Vote.objects.get_record('stonks')
        self.assertEqual(record.votes, -1)

    def test_downvote_via_alias(self):
        self.send_message('?-- stonks')
        self.send_message('?-- stonks')
        self.send_message('?-- stonks')
        record = Vote.objects.get_record('stonks')
        self.assertEqual(record.votes, -3)

    def test_festive_messages(self):
        with patch('plugins.votes.date') as mock_date:
            mock_date.today.return_value = date(2020, 10, 7)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            response = self.send_message('?upvote user')
            self.assertEqual('dummyuser upvoted user! user has 1 halloween candy', response)

    def test_festive_messages_dec(self):
        with patch('plugins.votes.date') as mock_date:
            mock_date.today.return_value = date(2020, 12, 7)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            response = self.send_message('?upvote user')
            self.assertEqual('dummyuser upvoted user! user has 1 candy cane', response)

    def test_nonfestive_messages(self):
        with patch('plugins.votes.date') as mock_date:
            mock_date.today.return_value = date(2020, 7, 7)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            response = self.send_message('?upvote user')
            self.assertEqual('dummyuser upvoted user! user has 1 friskypoint', response)

    def test_festive_messages_pl(self):
        self.send_message('?upvote user')
        with patch('plugins.votes.date') as mock_date:
            mock_date.today.return_value = date(2020, 10, 7)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            response = self.send_message('?upvote user')
            self.assertEqual('dummyuser upvoted user! user has 2 halloween candies', response)

    def test_festive_messages_dec_pl(self):
        self.send_message('?upvote user')
        with patch('plugins.votes.date') as mock_date:
            mock_date.today.return_value = date(2020, 12, 7)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            response = self.send_message('?upvote user')
            self.assertEqual('dummyuser upvoted user! user has 2 candy canes', response)

    def test_nonfestive_messages_pl(self):
        self.send_message('?upvote user')
        with patch('plugins.votes.date') as mock_date:
            mock_date.today.return_value = date(2020, 7, 7)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            response = self.send_message('?upvote user')
            self.assertEqual('dummyuser upvoted user! user has 2 friskypoints', response)

    def test_leaderboard(self):
        Vote.objects.create(label='foo', votes=3)
        Vote.objects.create(label='bar', votes=1)
        Vote.objects.create(label='foobar', votes=4)
        response = self.send_message('?leaderboard')
        self.assertEqual('*Upvote Leaderboard*\n'
                         'foobar: 4\n'
                         'foo: 3\n'
                         'bar: 1', response)

    def test_voting_across_channels_in_a_workspace(self):
        self.send_reaction('upvote', 'user_a', 'user_b', channel='channel1')
        self.send_reaction('upvote', 'user_a', 'user_b', channel='channel2')
        record = Vote.objects.get_record('user_b')
        self.assertEqual(record.votes, 2)
