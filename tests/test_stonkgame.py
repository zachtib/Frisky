from decimal import Decimal

import responses

from frisky.test import FriskyTestCase
from plugins.stonkgame import StonkGamePlugin
from stonkgame.models import StonkGame, StonkHolding
from .test_stock import positive_change, market_closed, negative_change

portfolio = '''
Total Holdings for player:
1 shares of GME ($420.69) total $420.69
69 shares of TSLA ($69.69) total $4808.61
4 shares of BB ($13.37) total $53.48
Total portfolio value: 5282.78. Cash on hand: 1000.00
'''.strip()

stock_response = '''
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
                                420.69
                            ]
                        }
                    ]
                }
            }
        ]
    }
}
'''.strip()

non_usd = '''
{
    "chart":{
        "result":[
            {
                "meta":{
                    "currency":"GBP",
                    "previousClose":42.00
                },
                "indicators":{
                    "quote":[
                        {
                            "close":[
                                420.69
                            ]
                        }
                    ]
                }
            }
        ]
    }
}
'''.strip()


class StonkGameTestCase(FriskyTestCase):

    def test_no_args_returns_help(self):
        result = self.send_message('?stonkgame')
        self.assertEqual(StonkGamePlugin.help, result)

    def test_creation_invalid_balance(self):
        result = self.send_message('?sg start potato')
        self.assertEqual('potato must be a valid decimal number', result)

    def test_creation(self):
        result = self.send_message('?sg start 100.00', channel='stonks')
        self.assertEqual(result, 'OK')
        game: StonkGame = StonkGame.objects.get(id=1)
        self.assertEqual(game.channel_name, 'stonks')
        self.assertEqual(game.starting_balance, Decimal('100.00'))

    def test_attempting_to_stonk_when_no_stonks_are_to_be_hand(self):
        result = self.send_message('?sg balance')
        self.assertEqual('No active game in this channel', result)

    def test_you_cant_join_twice(self):
        self.send_message('?sg start 100.00')
        self.send_message('?sg join')
        result = self.send_message('?sg join')
        self.assertEqual('You\'re already in the game, dummyuser', result)

    def test_joining(self):
        self.send_message('?sg start 100.00')
        result = self.send_message('?sg join')
        self.assertEqual('Welcome to the stonk game, dummyuser', result)

    def test_fetching(self):
        plugin = StonkGamePlugin()
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/GME'

        with responses.RequestsMock() as rm:
            rm.add('GET', url, body=stock_response)
            currency, amount, _ = plugin.get_stock_price('GME')
        self.assertEqual(currency, 'USD')
        self.assertEqual(amount, Decimal('420.69'))

    def test_checking_balance(self):
        self.send_message('?sg start 100.00', user='otheruser')
        self.send_message('?sg join')
        result = self.send_message('?sg balance')
        self.assertEqual(result, 'Your balance is $100.00')

    def test_checking_balance_before_joining(self):
        self.send_message('?sg start 100.00', user='otheruser')
        result = self.send_message('?sg balance')
        self.assertEqual(result, 'You haven\'t joined this game yet, try `?sg join`')

    def test_buying(self):
        game = StonkGame.objects.create(channel_name='testing', starting_balance='1000.00')
        game.players.create(username='player', balance='1000.00')
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/GME'
        with responses.RequestsMock() as rm:
            rm.add('GET', url, body=stock_response)
            result = self.send_message('?sg buy GME 1', user='player')
        self.assertEqual('Bought 1 share of GME', result)
        player = game.players.get(username='player')
        holding = player.holdings.get(symbol='GME')
        self.assertEqual(Decimal('579.31'), player.balance)
        self.assertEqual(holding.amount, 1)

    def test_selling(self):
        game = StonkGame.objects.create(channel_name='testing', starting_balance='1000.00')
        player = game.players.create(username='player', balance='1000.00')
        player.holdings.create(symbol='GME', amount=2)
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/GME'
        with responses.RequestsMock() as rm:
            rm.add('GET', url, body=stock_response)
            result = self.send_message('?sg sell GME 1', user='player')
        self.assertEqual('Sold 1 share of GME', result)
        player = game.players.get(username='player')
        holding = player.holdings.get(symbol='GME')
        self.assertEqual(Decimal('1420.69'), player.balance)
        self.assertEqual(holding.amount, 1)

    def test_selling_nothing(self):
        game = StonkGame.objects.create(channel_name='testing', starting_balance='1000.00')
        game.players.create(username='player', balance='1000.00')
        result = self.send_message('?sg sell GME 0', user='player')
        self.assertEqual('OK, I guess...', result)

    def test_buying_nothing(self):
        game = StonkGame.objects.create(channel_name='testing', starting_balance='1000.00')
        game.players.create(username='player', balance='1000.00')
        result = self.send_message('?sg buy GME 0', user='player')
        self.assertEqual('OK, I guess...', result)

    def test_selling_negative(self):
        game = StonkGame.objects.create(channel_name='testing', starting_balance='1000.00')
        game.players.create(username='player', balance='1000.00')
        result = self.send_message('?sg sell GME -1', user='player')
        self.assertEqual('I don\'t do negatives', result)

    def test_buying_negative(self):
        game = StonkGame.objects.create(channel_name='testing', starting_balance='1000.00')
        game.players.create(username='player', balance='1000.00')
        result = self.send_message('?sg buy GME -1', user='player')
        self.assertEqual('I don\'t do negatives', result)

    def test_buying_when_short_on_cash(self):
        game = StonkGame.objects.create(channel_name='testing', starting_balance='1000.00')
        game.players.create(username='player', balance='10.00')
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/GME'
        with responses.RequestsMock() as rm:
            rm.add('GET', url, body=stock_response)
            result = self.send_message('?sg buy GME 1', user='player')
        self.assertEqual('You don\'t have enough cash', result)

    def test_buying_defaults_to_one_share(self):
        game = StonkGame.objects.create(channel_name='testing', starting_balance='1000.00')
        game.players.create(username='player', balance='1000.00')
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/GME'
        with responses.RequestsMock() as rm:
            rm.add('GET', url, body=stock_response)
            result = self.send_message('?sg buy GME', user='player')
        self.assertEqual('Bought 1 share of GME', result)
        player = game.players.get(username='player')
        holding = player.holdings.get(symbol='GME')
        self.assertEqual(Decimal('579.31'), player.balance)
        self.assertEqual(holding.amount, 1)

    def test_selling_defaults_to_one_share(self):
        game = StonkGame.objects.create(channel_name='testing', starting_balance='1000.00')
        player = game.players.create(username='player', balance='1000.00')
        player.holdings.create(symbol='GME', amount=1)
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/GME'
        with responses.RequestsMock() as rm:
            rm.add('GET', url, body=stock_response)
            result = self.send_message('?sg sell GME', user='player')
        self.assertEqual('Sold 1 share of GME', result)
        player = game.players.get(username='player')
        with self.assertRaises(StonkHolding.DoesNotExist):
            player.holdings.get(symbol='GME')
        self.assertEqual(Decimal('1420.69'), player.balance)

    def test_buying_more_shares_than_you_have(self):
        game = StonkGame.objects.create(channel_name='testing', starting_balance='1000.00')
        player = game.players.create(username='player', balance='1000.00')
        player.holdings.create(symbol='GME', amount=1)
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/GME'
        with responses.RequestsMock() as rm:
            rm.add('GET', url, body=stock_response)
            result = self.send_message('?sg sell GME 2', user='player')
        self.assertEqual('You don\'t have enough shares', result)

    def test_invalid_command(self):
        result = self.send_message('?sg notacommand')
        self.assertEqual('I didn\'t understand that', result)

    def test_portfolio(self):
        game = StonkGame.objects.create(channel_name='testing', starting_balance='1000.00')
        player = game.players.create(username='player', balance='1000.00')
        player.holdings.create(symbol='GME', amount=1)
        player.holdings.create(symbol='TSLA', amount=69)
        player.holdings.create(symbol='BB', amount=4)
        gme = 'https://query1.finance.yahoo.com/v8/finance/chart/GME'
        tsla = 'https://query1.finance.yahoo.com/v8/finance/chart/TSLA'
        bb = 'https://query1.finance.yahoo.com/v8/finance/chart/BB'
        with responses.RequestsMock() as rm:
            rm.add('GET', gme, body=stock_response)
            rm.add('GET', tsla, body=positive_change)
            rm.add('GET', bb, body=negative_change)
            result = self.send_message('?sg portfolio', user='player')
        self.assertEqual(portfolio, result)

    def test_api_error(self):
        game = StonkGame.objects.create(channel_name='testing', starting_balance='1000.00')
        game.players.create(username='player', balance='1000.00')
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/GME'
        with responses.RequestsMock() as rm:
            rm.add('GET', url, status=404)
            result = self.send_message('?sg buy GME 1', user='player')
        self.assertEqual('I don\'t have any information for that stock', result)

    def test_api_error_sell(self):
        game = StonkGame.objects.create(channel_name='testing', starting_balance='1000.00')
        game.players.create(username='player', balance='1000.00')
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/GME'
        with responses.RequestsMock() as rm:
            rm.add('GET', url, status=404)
            result = self.send_message('?sg sell GME 1', user='player')
        self.assertEqual('I don\'t have any information for that stock', result)

    def test_non_usd(self):
        game = StonkGame.objects.create(channel_name='testing', starting_balance='1000.00')
        player = game.players.create(username='player', balance='1000.00')
        player.holdings.create(symbol='GME', amount=0)
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/GME'
        with responses.RequestsMock() as rm:
            rm.add('GET', url, body=non_usd)
            result = self.send_message('?sg buy GME 1', user='player')
        self.assertEqual('I only do dollars!', result)
        player = game.players.get(username='player')
        holding = player.holdings.get(symbol='GME')
        self.assertEqual(Decimal('1000.00'), player.balance)
        self.assertEqual(holding.amount, 0)

    def test_buying_when_closed(self):
        game = StonkGame.objects.create(channel_name='testing', starting_balance='1000.00')
        game.players.create(username='player', balance='1000.00')
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/GME'
        with responses.RequestsMock() as rm:
            rm.add('GET', url, body=market_closed)
            result = self.send_message('?sg buy GME 1', user='player')
        self.assertEqual('The market is closed, man.', result)
        player = game.players.get(username='player')
        self.assertEqual(Decimal('1000.00'), player.balance)
