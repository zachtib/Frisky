from typing import Optional, Tuple

import requests

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse


class StockPlugin(FriskyPlugin):

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'stock', 'stonk'

    @classmethod
    def help_text(cls) -> Optional[str]:
        return 'Usage: ?stock $SYMBOL'

    def format_url(self, symbol):
        return f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&includePrePost=false&interval=2m'

    def format_money(self, money, currency):
        if currency == 'USD':
            return f'${money:.2f}'
        raise NotImplementedError(f'Unsupported currency: {currency}')

    def get_chart_emoji(self, is_positive):
        if is_positive:
            return ':chart_with_upwards_trend:'
        else:
            return ':chart_with_downwards_trend:'

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        if len(message.args) < 1:
            return self.help_text()

        symbol = message.args[0]
        url = self.format_url(symbol)
        result = requests.get(url)
        if result.status_code == 200:
            json = result.json()
            currency = json['chart']['result'][0]['meta']['currency']
            last_close = json['chart']['result'][0]['meta']['previousClose']
            trades = json['chart']['result'][0]['indicators']['quote'][0]['close']
            last_trade = None
            while len(trades) and last_trade is None:
                last_trade = trades.pop()
            if last_trade is None:
                close_msg = f'{symbol} last closed at {self.format_money(last_close, currency)}'
                return close_msg
            diff = last_trade - last_close
            diff_perc = 100 * diff / last_close
            positive = diff > 0
            return f'{self.get_chart_emoji(positive)}{symbol} last traded at {last_trade} ({diff:.2f} {diff_perc:.2f}%)'
