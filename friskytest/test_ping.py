from frisky.test import FriskyTestCase


class PingTestCase(FriskyTestCase):

    def test_ping_returns_pong(self):
        reply = self.send_message('?ping')
        self.assertEqual('pong', reply)
