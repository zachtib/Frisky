import responses

from frisky.responses import Image
from frisky.test import FriskyTestCase
from learns.queries import add_learn
from memes.models import MemeAlias
from plugins.meme import MemePlugin


class MemeLearnTestCase(FriskyTestCase):

    def test_help(self):
        result = self.send_message('?memelearn help')
        self.assertEqual(result, 'Usage: `?memelearn <THING TO MEME>`')

    def test_alt_help(self):
        result = self.send_message('?help memelearn')
        self.assertEqual(result, 'Usage: `?memelearn <THING TO MEME>`')

    def test_nonexistant_meme(self):
        result = self.send_message('?memelearn foobar')
        self.assertEqual(result, 'NO SUCH MEME')

    def test_nonexistant_learn(self):
        MemeAlias.objects.create_alias('foobar', 12345)
        result = self.send_message('?memelearn foobar')
        self.assertEqual(result, 'NO SUCH LEARN')

    def test_success(self):
        with responses.RequestsMock() as rm:
            rm.add('POST', MemePlugin.CAPTION_IMAGE_URL, body='''{
                "success": true,
                "data": {
                    "url": "https://i.imgflip.com/123abc.jpg",
                    "page_url": "https://imgflip.com/i/123abc"
                }
            }'''.strip())

            MemeAlias.objects.create_alias('foobar', 12345)
            add_learn('foobar', 'xyzzy')

            result = self.send_message('?memelearn foobar')
            self.assertEqual(rm.calls[0].request.body,
                             'template_id=12345&username=&password=&text0=&' +
                             'text1=xyzzy')
            self.assertIsInstance(result, Image)
            self.assertEqual(result.url, 'https://i.imgflip.com/123abc.jpg')
