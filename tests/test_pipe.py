import responses

from frisky.responses import Image
from frisky.test import FriskyTestCase
from plugins.meme import MemePlugin


class PipeTestCase(FriskyTestCase):

    def test_pipe(self):
        self.send_message('?learn foo bar')
        self.send_message('?pipe foo | upvote')
        reply = self.send_message('?votes bar')
        self.assertTrue(reply.startswith('bar has 1 '))

    def test_piping_memes(self):
        self.send_message('?learn foo This Test Passed')
        self.send_message('?memealias goodnews 123456')

        with responses.RequestsMock() as rm:
            rm.add('POST', MemePlugin.CAPTION_IMAGE_URL, body='''
            {
                "success": true,
                "data": {
                    "url": "https://i.imgflip.com/123abc.jpg",
                    "page_url": "https://imgflip.com/i/123abc"
                }
            }
            '''.strip())
            reply = self.send_message('?pipe foo | meme goodnews "Good News Everyone"')
            self.assertEqual(rm.calls[0].request.body,
                             'template_id=123456&username=&password=&text0=Good+News+Everyone&' +
                             'text1=This+Test+Passed')
            self.assertIsInstance(reply, Image)
            self.assertEqual(reply.url, 'https://i.imgflip.com/123abc.jpg')

    def test_multi_piping(self):
        self.send_message('?learn foobar Hello, World')
        reply = self.send_message('?pipe foobar | format')
        self.assertEqual(reply, '')
