import re
from dataclasses import dataclass
from random import randint, normalvariate
from typing import Tuple, List, Optional

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse
from math import sqrt

@dataclass
class RollResult:
    result: int
    is_minimum: bool
    is_maximum: bool
    is_average: bool
    used_probability: bool

def clamp(num: int, min_value: int, max_value: int) -> int:
    return max(min(num, max_value), min_value)


@dataclass
class DieRoll:
    dice: int = 1
    sides: int = 20
    modifier: int = 0
    verbose: bool = True
    quiet: bool = False

    def mean(self) -> int:
        # https://boardgamegeek.com/blogpost/25470/variance-dice-sums
        #
        # example - average result of 2 6-sided dice:
        #   (2 * 6 + 2) / 2
        #   (12 + 2) / 2
        #   14 / 2
        #   7
        return (self.sides * self.dice + self.dice) / 2.0


    def variance(self) -> float:
        # Calculate the variance of one dice of `sides` first
        # Proof in roll.maxima: maxima < dice.maxima
        one_dice_variance = (self.sides**2 - 1) / 12.0
        return self.dice * one_dice_variance


    def regular_roll(self) -> int:
        total = 0
        for i in range(0, self.dice):
            result = randint(1, self.sides)
            total += result
        if self.modifier:
            total += self.modifier
        return total

    def probability_roll(self) -> int:
        m = self.mean()
        v = self.variance()
        standard_deviation = sqrt(v)
        result = normalvariate(m, standard_deviation)
        return clamp(round(result), self.sides, self.sides * self.dice) + self.modifier

    def probability_of(self, n: int) -> float:
        if self.dice == 1:
            return 1 / self.sides
        m = self.mean()
        v = self.variance()
        


    def roll(self) -> RollResult:
        s = 0
        if self.dice > 10000:
            s = self.probability_roll()
        else:
            s = self.regular_roll()

        return RollResult(
            result = s,
            is_minimum = (s == self.dice + self.modifier),
            is_maximum = (s == self.dice * self.sides + self.modifier),
            is_average = (s == self.mean()),
            used_probability = self.dice > 10000
        )


regex = re.compile(r'(\d+)?d(\d+)([+\-]\d+)?')


def parse_single_die_syntax(expr: str) -> Optional[DieRoll]:
    m = regex.match(expr)
    if m is None:
        return None
    return DieRoll(
        dice=int(m.group(1) or 1),  # Default to rolling 1 die,
        sides=int(m.group(2)),  # This is the only hard required value
        modifier=int(m.group(3) or 0)  # Default to zero modifier
    )


def parse_dice_syntax(inputs: List[str]) -> List[DieRoll]:
    return [parse_single_die_syntax(expr) for expr in inputs]


class RollPlugin(FriskyPlugin):

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'roll',

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        if len(message.args) == 0:
            # With no inputs, default to rolling 1d20
            d20 = DieRoll(dice=1, sides=20)
            roll = d20.roll().result
            return f'Rolling 1d20 for {message.username}: {roll}'

        parsed_rolls = parse_dice_syntax(message.args)
        results = []
        errors = []
        for expr, roll in zip(message.args, parsed_rolls):
            if roll is None:
                errors.append(expr)
                results.append('???')
            elif roll.dice <= 10000:
                results.append(f"{roll.roll().result}")
            else:
                results.append(f"{roll.roll().result} USING MATH")

        result_string = ', '.join(results)
        errors_string = ', '.join(errors)
        message = f'{message.username} rolled {result_string}'
        if errors_string:
            message += f"... I don't know how to roll {errors_string}"
        return message
