from frisky.test import FriskyTestCase
from votes.queries import get_votes_record


class VoteTestCase(FriskyTestCase):

    def test_upvote_user_has_one_vote(self):
        self.send_reaction('upvote', 'user_a', 'user_b')
        record = get_votes_record('user_b')
        self.assertEqual(record.votes, 1)

    def test_vote_query(self):
        reply = self.send_message('?votes user_b')
        self.assertEqual(reply, 'user_b has 0 votes')
