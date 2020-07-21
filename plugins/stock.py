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
            if money >= 0:
                return f'${money:.2f}'
            else:
                money *= -1
                return f'-${money:.2f}'
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
        response = requests.get(url)
        if response.status_code == 200:
            json = response.json()
            result = json['chart']['result'][0]
            currency = result['meta']['currency']
            last_close = result['meta']['previousClose']
            trades = result['indicators']['quote'][0]['close']
            if len(trades):
                last_trade = trades.pop()
                daily_change = last_trade - last_close
                percentage_change = 100 * daily_change / last_close
                is_positive = daily_change > 0
                return f'{self.get_chart_emoji(is_positive)}  {symbol} last traded at ' \
                       f'{self.format_money(last_trade, currency)} ' \
                       f'({self.format_money(daily_change, currency)} {percentage_change:.2f}%)'
            else:
                close_msg = f'{symbol} last closed at {self.format_money(last_close, currency)}'
                return close_msg
