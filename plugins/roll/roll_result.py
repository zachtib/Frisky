from dataclasses import dataclass

@dataclass
class RollResult:
    result: int
    is_minimum: bool
    is_maximum: bool
    is_average: bool
    used_probability: bool
    chance: float
    chance_ish: float
