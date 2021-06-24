from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse

from .models import BetterStonkGame


class StonksPlugin(FriskyPlugin):
    commands = [
        "stonkifyme"
    ]

    def command_stonkifyme(self, message: MessageEvent) -> FriskyResponse:
        game = BetterStonkGame.objects.first()
        return "Hello, there"
