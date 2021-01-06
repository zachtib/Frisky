from dataclasses import dataclass
from typing import Union, Optional


@dataclass
class Image:
    url: str
    alt_text: str = ""


@dataclass
class FriskyError:
    message: str


FriskyResponse = Optional[Union[Image, str, FriskyError]]
