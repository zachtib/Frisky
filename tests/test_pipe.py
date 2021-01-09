import responses

from apilearns.models import ApiLearn
from frisky.responses import Image
from frisky.test import FriskyTestCase
from learns.models import Learn
from plugins.meme import MemePlugin


class PipeTestCase(FriskyTestCase):

    def test_pipe(self):
        self.send_message('?learn foo bar')
        self.send_message('?pipe foo | upvote')
        reply = self.send_message('?votes bar')
        self.assertTrue(reply.startswith('bar has 1 '))

    def test_piping_when_multiple_plugins_handle_generic(self):
        ApiLearn.objects.create(label='foo', url='https://example.com/')
        Learn.objects.create(label='foo', content='bar')
        actual = self.send_message("?pipe foo | bar")
        self.assertEqual(actual, 'Too many plugins returned a response for foo')

    def test_piping_when_no_plugins_handle_generic(self):
        actual = self.send_message("?pipe foo | bar")
        self.assertEqual(actual, 'No plugins returned a response for foo')

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
