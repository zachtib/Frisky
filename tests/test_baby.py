import responses

from frisky.test import FriskyTestCase

URL = "https://hasasiahadthebabyyet.herokuapp.com/api/"
YEP_RESPONSE = '''
{
    "display": "Yep."
}'''
NOPE_RESPONSE = '''
{
    "display": "Nope."
}'''
EMPTY_JSON = '{}'


class StockTestCase(FriskyTestCase):

    def test_empty(self):
        with responses.RequestsMock() as rm:
            rm.add('GET', URL, body=EMPTY_JSON)
            reply = self.send_message('?baby')
            self.assertEqual(reply, None)

    def test_yep(self):
        with responses.RequestsMock() as rm:
            rm.add('GET', URL, body=YEP_RESPONSE)
            reply = self.send_message('?baby')
            self.assertEqual(reply, 'Yep.')

    def test_nope(self):
        with responses.RequestsMock() as rm:
            rm.add('GET', URL, body=NOPE_RESPONSE)
            reply = self.send_message('?baby')
            self.assertEqual(reply, 'Nope.')
