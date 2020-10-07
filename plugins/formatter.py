from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin


class FormatterPlugin(FriskyPlugin):

    commands = ['format']

    def command_format(self, message: MessageEvent) -> FriskyPlugin:
        return message.text