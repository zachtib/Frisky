from random import randint
from typing import Tuple

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse


class RollPlugin(FriskyPlugin):

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'roll',

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        dice = []
        for arg in message.args:
            try:
                int_arg = int(arg)
                if int_arg > 1:
                    dice.append(int_arg)
            except ValueError:
                pass
        if len(dice) == 0:
            dice = [20]
        results = []
        for die in dice:
            result = randint(1, die)
            results.append(str(result))
        result_string = ', '.join(results)
        return f'{message.username} rolled {result_string}'
