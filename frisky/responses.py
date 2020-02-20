from dataclasses import dataclass
from typing import Union, Optional


@dataclass
class Image:
    url: str
    alt_text: str = ""


FriskyResponse = Optional[Union[Image, str]]
