from friskytest import FriskyTestCase


class PingTestCase(FriskyTestCase):

    def test_ping_returns_poing(self):
        reply = self.send_message('?ping')
        self.assertEqual('pong', reply)
