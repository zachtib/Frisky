from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse


class StonksPlugin(FriskyPlugin):
    commands = [
        "stonkifyme"
    ]

    def command_stonkifyme(self, message: MessageEvent) -> FriskyResponse:
        return "Hello, there"
