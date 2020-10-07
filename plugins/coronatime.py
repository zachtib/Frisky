from datetime import date, timedelta

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse


class CoronaTimePlugin(FriskyPlugin):
    commands = ['coronatime']

    help = 'Formats the date in UTC (Universal Time Corona)'

    def ord(self, n):
        return str(n) + ("th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))

    def calc_coronatime(self, origin, today):
        delta: timedelta = today - origin
        days = delta.days + 1

        return f'It is the {self.ord(days)} of March, 2020'

    def command_coronatime(self, _: MessageEvent) -> FriskyResponse:
        origin = date(2020, 3, 1)
        today = date.today()

        if today < origin:
            return
        return self.calc_coronatime(origin, today)
