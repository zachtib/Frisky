from dataclasses import dataclass, field
from typing import Optional, List, Dict
from frisky.models import Workspace, Channel, Member


@dataclass
class MessageEvent(object):
    workspace: Workspace
    channel: Channel
    user: Member
    users: Dict[str, Member]
    raw_message: Optional[str]
    username: str
    channel_name: str
    text: Optional[str]
    command: str = ""
    args: List[str] = field(default_factory=list)


@dataclass
class ReactionEvent(object):
    workspace: Workspace
    channel: Channel
    user: Member
    users: Dict[str, Member]
    emoji: str
    username: str
    added: bool
    message: MessageEvent
