from decimal import Decimal, InvalidOperation
from typing import Tuple

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse
from stonkgame.models import StonkGame, StonkPlayer


class StockNotFoundException(Exception):
    pass


class StonkException(Exception):
    def __init__(self, message):
        self.message = message


class StonkGamePlugin(FriskyPlugin):
    help = 'Play the Stonk Game!'

    commands = ['stonkgame']

    command_aliases = {
        'sg': 'stonkgame',
    }

    def command_stonkgame(self, message: MessageEvent) -> FriskyResponse:
        if len(message.args) == 0:
            return self.help
        command = message.args[0]
        channel_name = message.channel_name

        try:
            if command == 'start':
                return self.__start(message.channel_name, message.args[1])
            elif command == 'join':
                return self.__join(channel_name, message.username)
            elif command == 'balance':
                return self.__balance(message.channel_name, message.username)
            elif command == 'buy':
                return self.__buy(
                    message.channel_name,
                    message.username,
                    message.args[1],
                    int(message.args[2]) if 2 < len(message.args) else 1
                )
            elif command == 'sell':
                return self.__sell(
                    message.channel_name,
                    message.username,
                    message.args[1],
                    int(message.args[2]) if 2 < len(message.args) else 1
                )
            elif command == 'portfolio':
                return self.__portfolio(message.channel_name, message.username)
            return 'I didn\'t understand that'
        except StonkGame.DoesNotExist:
            return 'No active game in this channel'
        except StonkPlayer.DoesNotExist:
            return 'You haven\'t joined this game yet, try `?sg join`'
        except StonkException as e:
            return e.message

    def __start(self, channel_name: str, starting_balance: str) -> FriskyResponse:
        try:
            starting_balance = Decimal(starting_balance)
        except InvalidOperation:
            return f'{starting_balance} must be a valid decimal number'
        StonkGame.objects.create(channel_name=channel_name, starting_balance=starting_balance)
        return 'OK'

    def __join(self, channel_name: str, player_name: str) -> FriskyResponse:
        game: StonkGame = StonkGame.objects.get(channel_name=channel_name)
        player, created = game.players.get_or_create(username=player_name, defaults={
            'balance': game.starting_balance
        })
        if created:
            return f'Welcome to the stonk game, {player.username}'
        else:
            return f'You\'re already in the game, {player.username}'

    def get_stock_price(self, symbol) -> Tuple[str, Decimal, bool]:
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&includePrePost=false&interval=2m'
        response = self.http.get(url)
        if response.status_code == 200:
            json = response.json()
            result = json['chart']['result'][0]
            currency = result['meta']['currency']
            last_close = result['meta']['previousClose']
            trades = result['indicators']['quote'][0]['close']
            if len(trades):
                return currency, round(Decimal(trades.pop()), 2), True
            else:
                return currency, round(Decimal(last_close), 2), False
        raise StockNotFoundException()

    def __balance(self, channel_name, username):
        game = StonkGame.objects.get(channel_name=channel_name)
        player = game.players.get(username=username)
        return f'Your balance is ${player.balance}'

    def __prep_transaction(self, channel_name: str, username: str, symbol: str, amount: int):
        game = StonkGame.objects.get(channel_name=channel_name)
        player = game.players.get(username=username)
        currency, stock_price, market_open = self.get_stock_price(symbol)
        if not market_open:
            raise StonkException('The market is closed, man.')
        if currency != 'USD':
            raise StonkException('I only do dollars!')
        holding, created = player.holdings.get_or_create(symbol=symbol, defaults={
            'amount': 0,
        })
        price: Decimal = stock_price * amount
        return player, holding, price

    def __buy(self, channel_name: str, username: str, symbol: str, amount: int):
        if amount == 0:
            return 'OK, I guess...'
        if amount < 0:
            return 'I don\'t do negatives'
        symbol = symbol.upper()
        try:
            player, holding, price = self.__prep_transaction(channel_name, username, symbol, amount)
        except StockNotFoundException:
            return 'I don\'t have any information for that stock'
        if player.balance < price:
            return 'You don\'t have enough cash'
        player.balance -= price
        holding.amount += amount
        player.save()
        holding.save()
        return f'Bought {amount} share of {symbol}'

    def __sell(self, channel_name: str, username: str, symbol: str, amount: int):
        if amount == 0:
            return 'OK, I guess...'
        if amount < 0:
            return 'I don\'t do negatives'
        symbol = symbol.upper()
        try:
            player, holding, price = self.__prep_transaction(channel_name, username, symbol, amount)
        except StockNotFoundException:
            return 'I don\'t have any information for that stock'
        if holding.amount < amount:
            return 'You don\'t have enough shares'
        player.balance += price
        holding.amount -= amount
        player.save()
        holding.save()
        if holding.amount == 0:
            holding.delete()
        return f'Sold {amount} share of {symbol}'

    def __portfolio(self, channel_name: str, username: str):
        game = StonkGame.objects.get(channel_name=channel_name)
        player = game.players.get(username=username)
        responses = [f'Total Holdings for {username}:']
        running_total = Decimal('0.00')
        for holding in player.holdings.all():
            currency, stock_price, _ = self.get_stock_price(holding.symbol)
            total_value = stock_price * holding.amount
            responses += [f'{holding.amount} shares of {holding.symbol} (${stock_price}) total ${total_value}']
            running_total += total_value
        responses += [f'Total portfolio value: {running_total}. Cash on hand: {player.balance}']
        return '\n'.join(responses)
