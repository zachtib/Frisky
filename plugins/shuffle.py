from random import randint
from typing import Tuple

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse


class ShufflePlugin(FriskyPlugin):

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'shuffle',

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        values = list(message.args)
        output = []

        while len(values):
            index = randint(0, len(values) - 1)
            output.append(values.pop(index))

        return ', '.join(output)
