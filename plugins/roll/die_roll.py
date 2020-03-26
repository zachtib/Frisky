import re
from random import randint, normalvariate
from dataclasses import dataclass
from math import sqrt, erf, floor
from typing import Optional

from .roll_result import RollResult

def clamp(num: int, min_value: int, max_value: int) -> int:
    return max(min(num, max_value), min_value)


@dataclass
class DieRoll:
    dice: int = 1
    sides: int = 20
    modifier: int = 0
    stats: bool = True

    @staticmethod
    def parse(msg: str) -> Optional['DieRoll']:
        regex = re.compile(r'(\d+)?d(\d+)([+\-]\d+)?(q?)')
        m = regex.match(msg)
        if m is None:
            return None
        return DieRoll(
            dice = int(m.group(1) or 1),  # Default to rolling 1 die,
            sides = int(m.group(2)),  # This is the only hard required value
            modifier = int(m.group(3) or 0),  # Default to zero modifier
            stats = m.group(4) != 'q',
        )

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
        total += self.modifier
        return total


    def probability_roll(self) -> int:
        m = self.mean()
        v = self.variance()
        standard_deviation = sqrt(v)
        result = normalvariate(m, standard_deviation)
        return clamp(round(result), self.sides, self.sides * self.dice) + self.modifier


    def chance_dice_exactly_equals(self, n: int, k: int, cache = None) -> float:
        # The computation is too slow without a cache
        if cache == None:
            cache = dict()
        if n <= 1:
            if k < 1 or k > self.sides: # You can't roll a 7 on a 6-sided die
                return 0
            return 1 / self.sides
        else:
            result = 0
            for i in range(1, k - n + 2):
                # we are looking for 'i' on the first dice
                # and 'k - i' on the remaining dice
                # if 'k - i' > (n - 1) * sides, this is zero
                if k - i <= (n - 1) * self.sides:
                    if (n - 1, k - i) not in cache:
                        cache[(n - 1, k - i)] = self.chance_dice_exactly_equals(n - 1, k - i, cache)
                    result += self.chance_dice_exactly_equals(1, i, cache) * cache[(n - 1, k - i)]
            return result


    def cdf(self, r: float) -> float:
        if self.sides <= 50 and self.dice <= 4:
            r = floor(r)
            result = 0
            for i in range(1, int(r) + 1):
                result += self.chance_dice_exactly_equals(self.dice, i)
            return result
            
        # Well, I think this method is clear to anyone who sees it.
        #
        # In case it's not, this is an approximation function for the probability
        # of an n s-sided dice roll having the value below 'r'
        # This is proven as a float-equivilent version in dice.maxima, assuming
        # that dice rolls follow a normal distribution
        # (which they don't, but they approach a normal distribution very
        # quickly as n rises)
    
        n = self.dice
        s = self.sides
        return (0.3989422804014326 *
                    (0.3618006272791339 *
                        sqrt(n * s ** 2 - 1.0 * n) * 
                        2.718281828459045 **
                            ((-(3 * n * s ** 2) /
                                (2 * s ** 2 - 2)) -
                            (3 * n) /
                            (2 * s ** 2 - 2) -
                            (3 * n * s) /
                            (s ** 2 - 1) +
                            (3 * n * s) /
                            (2 * s - 2) +
                            (3 * n) /
                            (2 * s - 2)) *
                        erf((3.0 * sqrt(n * s ** 2 - 1.0 * n)) /
                            (2.449489742783178 * s-2.449489742783178)) -
                        0.3618006272791339 * sqrt(n * s ** 2 - 1.0 * n) *
                        2.718281828459045 ** (
                            (-(3 * n * s**2) /
                                (2 * s ** 2 - 2)) -
                            (3 * n) /
                            (2 * s ** 2 - 2) -
                            (3 * n * s) /
                            (s ** 2 - 1) +
                            (3 * n * s) /
                            (2 * s - 2) +
                            (3 * n) /
                            (2 * s - 2)
                        ) *
                        erf((0.4082482904638631 * (3.0 * n * s - 6.0 * r + 3.0 * n)) /
                            sqrt(n * s ** 2 - 1.0 * n)
                        )
                    )
                ) / sqrt(
                    (n * (
                            0.25 * s ** 3 + 0.5 * s ** 2 +
                            0.1666666666666667 * s * (s + 1.0) *
                            (2.0 * s + 1.0) -
                            0.5 * s ** 2 *
                            (s+1.0) -
                            0.5 * s *
                            (s+1.0) +
                            0.25 * s
                        )
                    ) /
                s)


    def probability_eq(self, r: int) -> float:
        if self.dice < 1:
            return 1.0
        elif self.dice == 1:
            return 1 / self.sides
        return self.cdf(r + 0.5) - self.cdf(r - 0.5)


    def probability_ge(self, r: int) -> float:
        if self.dice < 1:
            return 1.0
        elif self.dice == 1:
            return (self.sides - r) / self.sides
        return 1.0 - self.cdf(r - 0.5)


    def probability_le(self, r: int) -> float:
        if self.dice < 1:
            return 1.0
        elif self.dice == 1:
            return r / self.sides
        return self.cdf(r + 0.5)


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
            chance = self.probability_eq(s - self.modifier),
            chance_ish = (self.sides > 50 or self.dice > 4) and self.dice != 1,
            used_probability = self.dice > 10000
        )
