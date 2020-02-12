from frisky.test import FriskyTestCase
from votes.queries import get_votes_record


class VoteTestCase(FriskyTestCase):

    def test_upvote_user_has_one_vote(self):
        self.send_reaction('upvote', 'user_a', 'user_b')
        record = get_votes_record('user_b')
        self.assertEqual(record.votes, 1)

    def test_downvote_user_has_neg_one_vote(self):
        self.send_reaction('downvote', 'user_a', 'user_b')
        record = get_votes_record('user_b')
        self.assertEqual(record.votes, -1)

    def test_vote_query(self):
        reply = self.send_message('?votes user_b')
        self.assertTrue(reply.startswith('user_b has 0'))
        record = get_votes_record('user_b')
        self.assertEqual(record.votes, 0)

    def test_upvote_via_cmd(self):
        self.send_message('?upvote stonks')
        record = get_votes_record('stonks')
        self.assertEqual(record.votes, 1)

    def test_upvote_via_alias(self):
        self.send_message('?++ stonks')
        self.send_message('?++ stonks')
        self.send_message('?++ stonks')
        record = get_votes_record('stonks')
        self.assertEqual(record.votes, 3)

    def test_downvote_via_cmd(self):
        self.send_message('?downvote stonks')
        record = get_votes_record('stonks')
        self.assertEqual(record.votes, -1)

    def test_downvote_via_alias(self):
        self.send_message('?-- stonks')
        self.send_message('?-- stonks')
        self.send_message('?-- stonks')
        record = get_votes_record('stonks')
        self.assertEqual(record.votes, -3)
