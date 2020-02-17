from frisky.test import FriskyTestCase


class MemeTestCase(FriskyTestCase):

    def test_entrypoint(self):
        reply = self.send_message('?meme "One Does Not Simply" "One Does Not Simply" "Mock Http Requests"')
        self.assertTrue(reply.startswith('http'))
