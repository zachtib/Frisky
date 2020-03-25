import re
from dataclasses import dataclass
from math import sqrt
from random import normalvariate, randint
from typing import Tuple, List, Optional

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse

@dataclass
class DieRoll:
    count: int
    die: int
    modifier: int = 0


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


def mean(sides: int, dice: int) -> float:
    # https://boardgamegeek.com/blogpost/25470/variance-dice-sums
    #
    # example - average result of 2 6-sided dice:
    #   (2 * 6 + 2) / 2
    #   (12 + 2) / 2
    #   14 / 2
    #   7
    return (sides * dice + dice) / 2.0


def variance(sides: int, dice: int) -> float:
    # Calculate the variance of once dice of `sides` first
    # Proof in roll.maxima: maxima < roll.maxima
    one_dice_variance = (sides**2 - 1) / 12.0
    return dice * one_dice_variance


def clamp(num: int, min_value: int, max_value: int) -> int:
    return max(min(num, max_value), min_value)


def probability_roll(roll: DieRoll) -> int:
    m = mean(roll.die, roll.count)
    v = variance(roll.die, roll.count)
    standard_deviation = sqrt(v)
    result = normalvariate(m, standard_deviation)
    return clamp(round(result), roll.die, roll.die * roll.count) + roll.modifier


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
            elif roll.count <= 10000:
                results.append(f"{calculate_roll(roll)}")
            else:
                results.append(f"{probability_roll(roll)} USING MATH")
        result_string = ', '.join(results)
        errors_string = ', '.join(errors)
        message = f'{message.username} rolled {result_string}'
        if errors_string:
            message += f"... I don't know how to roll {errors_string}"
        return message
