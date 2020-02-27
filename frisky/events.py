from dataclasses import dataclass
from typing import Tuple


@dataclass
class MessageEvent(object):
    username: str
    channel_name: str
    text: str
    command: str = ""
    args: Tuple[str] = tuple()


@dataclass
class ReactionEvent(object):
    emoji: str
    username: str
    added: bool
    message: MessageEvent
