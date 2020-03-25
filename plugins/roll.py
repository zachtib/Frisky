import re
from dataclasses import dataclass
from random import randint
from typing import Tuple, List, Optional

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse


@dataclass
class DieRoll:
    count: int
    die: int
    modifier: Optional[int] = None


regex = re.compile(r'(\d+)?d(\d+)([+\-]\d+)?')


def parse_single_die_syntax(expr: str) -> Optional[DieRoll]:
    m = regex.match(expr)
    if m is None:
        return None
    return DieRoll(
        count=int(m.group(1) or 1),  # Default to rolling 1 die,
        die=int(m.group(2)),  # This is the only hard required value
        modifier=int(m.group(3) or 0)  # Default to zero modifier
    )


def parse_dice_syntax(inputs: List[str]) -> List[DieRoll]:
    return [parse_single_die_syntax(expr) for expr in inputs]


def calculate_roll(roll: DieRoll) -> int:
    total = 0
    for i in range(0, roll.count):
        result = randint(1, roll.die)
        total += result
    if roll.modifier:
        total += roll.modifier
    return total


class RollPlugin(FriskyPlugin):

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'roll',

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        if len(message.args) == 0:
            # With no inputs, default to rolling 1d20
            d20 = DieRoll(count=1, die=20)
            roll = calculate_roll(d20)
            return f'Rolling 1d20 for {message.username}: {roll}'

        parsed_rolls = parse_dice_syntax(message.args)
        results = []
        errors = []
        for expr, roll in zip(message.args, parsed_rolls):
            if roll is None:
                errors.append(expr)
                results.append('???')
            elif roll.count > 1000:
                return "I don't have that many dice, man!"
            elif roll.die > 1000:
                return "I don't have a die that big, man!"
            else:
                results.append(str(calculate_roll(roll)))
        result_string = ', '.join(results)
        errors_string = ', '.join(errors)
        message = f'{message.username} rolled {result_string}'
        if errors_string:
            message += f"... I don't know how to roll {errors_string}"
        return message
