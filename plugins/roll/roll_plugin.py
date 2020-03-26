import re
from typing import Tuple, List, Optional

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse
from .roll_result import RollResult
from .die_roll import DieRoll

def parse_dice_syntax(inputs: List[str]) -> List[DieRoll]:
    return [DieRoll.parse(expr) for expr in inputs]


class RollPlugin(FriskyPlugin):

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'roll',

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        parsed_rolls = []
        args = []
        if len(message.args) == 0:
            # With no inputs, default to rolling 1d20
            d20 = DieRoll(dice=1, sides=20)
            roll = d20.roll().result

            # place the D20 into parsed rolls
            parsed_rolls = [DieRoll(dice=1, sides=20)]
            args = ["1d20"]
        else:
            parsed_rolls = parse_dice_syntax(message.args)
            args = message.args

        results = []
        errors = []
        total = 0
        for expr, roll in zip(args, parsed_rolls):
            if roll is None:
                errors.append(expr)
                results.append('???')
            else:
                # We want a message in the format "1d4+1 and it's a 5" in the variable 'quiet'
                result = roll.roll()
                modifier = ""
                if roll.modifier < 0:
                    modifier = str(roll.modifier)
                if roll.modifier > 0:
                    modifier = "+" + str(roll.modifier)
                quiet = f"{result.result} on {roll.dice}d{roll.sides}{modifier}"
                
                # if the value is a minimum or maximum, turn that into a string for the user
                # and put it in 'critical'
                critical = ""
                if result.is_minimum:
                    critical = "CRITICAL FAIL "
                if result.is_maximum:
                    critical = "CRITICAL "
                total += result.result
                # Did we "use math" to compute the result of the dice roll?
                using_math = ""
                if result.used_probability:
                    using_math = "USING MATH "

                # We calculate the chance of the dice roll.  Because this cannot be done for large
                # numbers of dice or large sided-dice.  We also estimate the probability for the user.
                # If this is an estimate, add "ish" to the end of the estimate
                ish = ""
                if result.chance_ish:
                    ish = "ish"

                # generate the float string out to 8 decimal digits, but strip the 0's to the right
                chance_string = f'{(result.chance*100):.8f}'.rstrip('0')

                # if there's a period at the end, remove that too
                chance_string = chance_string.rstrip('.')

                # The verbose string should read "CRITICAL 5 on 1d4+1 with a chance of 25%"
                verbose = f"{critical}{result.result} {using_math}on {roll.dice}d{roll.sides}{modifier} with a chance of {chance_string}%{ish}"

                # If the user specified quiet, only return the quiet string.  Otherwise, return
                # the full string
                if roll.stats:
                    results.append(verbose)
                else:
                    results.append(quiet)

        result_string = ', '.join(results)
        errors_string = ', '.join(errors)

        total_string = ""
        if len(parsed_rolls) > 1:
            total_string = f" for a total of {total}"
        message = f'{message.username} rolled {result_string}{total_string}'
        if errors_string:
            message += f"... I don't know how to roll {errors_string}"
        return message
