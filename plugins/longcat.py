from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse


class LongcatPlugin(FriskyPlugin):

    commands = ['longcat']
    help = 'Create the longest of cats'

    def command_longcat(self, message: MessageEvent) -> FriskyResponse:
        if len(message.args) != 1:
            return
        try:
            count = int(message.args[0])
        except ValueError:
            return
        return '\n'.join([':longcat-begin:'] + [':longcat-middle:'] * count + [':longcat-end:'])
