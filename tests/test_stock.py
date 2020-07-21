import responses

from frisky.test import FriskyTestCase


positive_change = '''
{
    "chart":{
        "result":[
            {
                "meta":{
                    "currency":"USD",
                    "previousClose":42.00
                },
                "indicators":{
                    "quote":[
                        {
                            "close":[
                                69.69
                            ]
                        }
                    ]
                }
            }
        ]
    }
}
'''.strip()

negative_change = '''
{
    "chart":{
        "result":[
            {
                "meta":{
                    "currency":"USD",
                    "previousClose":42.00
                },
                "indicators":{
                    "quote":[
                        {
                            "close":[
                                13.37
                            ]
                        }
                    ]
                }
            }
        ]
    }
}
'''.strip()

market_closed = '''
{
    "chart":{
        "result":[
            {
                "meta":{
                    "currency":"USD",
                    "previousClose":420.69
                },
                "indicators":{
                    "quote":[
                        {
                            "close":[
                            ]
                        }
                    ]
                }
            }
        ]
    }
}
'''.strip()


class StockTestCase(FriskyTestCase):

    URL = 'https://query1.finance.yahoo.com/v8/finance/chart/TEST'

    def test_stock_market_closed(self):
        with responses.RequestsMock() as rm:
            rm.add('GET', StockTestCase.URL, body=market_closed)
            reply = self.send_message('?stock TEST')
            self.assertEqual(reply, 'TEST last closed at $420.69')

    def test_positive_change(self):
        with responses.RequestsMock() as rm:
            rm.add('GET', StockTestCase.URL, body=positive_change)
            reply = self.send_message('?stock TEST')
            self.assertEqual(reply, ':chart_with_upwards_trend:  TEST last traded at $69.69 ($27.69 65.93%)')

    def test_negative_change(self):
        with responses.RequestsMock() as rm:
            rm.add('GET', StockTestCase.URL, body=negative_change)
            reply = self.send_message('?stock TEST')
            self.assertEqual(reply, ':chart_with_downwards_trend:  TEST last traded at $13.37 (-$28.63 -68.17%)')
