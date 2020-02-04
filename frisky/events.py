from dataclasses import dataclass
from typing import Tuple


@dataclass
class MessageEvent(object):
    username: str
    channel_name: str
    text: str
    tokens: Tuple[str]


@dataclass
class ReactionEvent(object):
    emoji: str
    username: str
    added: bool
    message: MessageEvent
