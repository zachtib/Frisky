from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class MessageEvent(object):
    username: str
    channel_name: str
    text: Optional[str]
    command: str = ""
    args: List[str] = field(default_factory=list)


@dataclass
class ReactionEvent(object):
    emoji: str
    username: str
    added: bool
    message: MessageEvent
