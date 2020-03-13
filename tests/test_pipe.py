from frisky.test import FriskyTestCase


class PipeTestCase(FriskyTestCase):

    def test_pipe(self):
        self.send_message('?learn foo bar')
        self.send_message('?pipe foo | upvote')
        reply = self.send_message('?votes bar')
        self.assertTrue(reply.startswith('bar has 1 '))
