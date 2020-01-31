from dataclasses import dataclass
from typing import List, Dict

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class RateLimitedEvent(object):
    """
    {
        "token": "Jhj5dZrVaK7ZwHHjRyZWjbDl",
        "type": "app_rate_limited",
        "team_id": "T123456",
        "minute_rate_limited": 1518467820,
        "api_app_id": "A123456"
    }
    """
    token: str
    type: str
    team_id: str
    minute_rate_limited: int
    api_app_id: str


@dataclass_json
@dataclass
class Event(object):
    """
    The Slack Event wrapper. An example:

    {
            "token": "z26uFbvR1xHJEdHE1OQiO6t8",
            "team_id": "T061EG9RZ",
            "api_app_id": "A0FFV41KK",
            "event": {
                    "type": "reaction_added",
                    "user": "U061F1EUR",
                    "item": {
                            "type": "message",
                            "channel": "C061EG9SL",
                            "ts": "1464196127.000002"
                    },
                    "reaction": "slightly_smiling_face",
                    "item_user": "U0M4RL1NY",
                    "event_ts": "1465244570.336841"
            },
            "type": "event_callback",
            "authed_users": [
                    "U061F7AUR"
            ],
            "event_id": "Ev9UQ52YNA",
            "event_time": 1234567890
    }
    """
    token: str
    team_id: str
    api_app_id: str
    event: Dict[str, any]
    type: str
    authed_users: List[str]
    event_id: str
    event_time: int

    def get_event(self):
        event_type = self.event.get('type', None)
        if event_type == 'reaction_added':
            return ReactionAdded.from_dict(self.event)
        return None


@dataclass_json
@dataclass
class ReactionItem(object):
    """
    {
        "type": "message",
        "channel": "C061EG9SL",
        "ts": "1464196127.000002"
    }
    """
    type: str
    channel: str
    ts: str


@dataclass_json
@dataclass
class ReactionAdded(object):
    """
    {
        "type": "reaction_added",
        "user": "U061F1EUR",
        "item": {
            "type": "message",
            "channel": "C061EG9SL",
            "ts": "1464196127.000002"
        },
        "reaction": "slightly_smiling_face",
        "item_user": "U0M4RL1NY",
        "event_ts": "1465244570.336841"
    }
    """
    type: str
    user: str
    item: ReactionItem
    reaction: str
    item_user: str
    event_ts: str
