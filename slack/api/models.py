from dataclasses import dataclass
from typing import List, Dict, Optional

from dataclasses_json import DataClassJsonMixin


class BaseModel(DataClassJsonMixin):
    def key(self):
        if hasattr(self, 'id'):
            return self.create_key(getattr(self, 'id'))
        return None

    @classmethod
    def create_key(cls, *args):
        return cls.__name__ + ':' + ':'.join(args)

    @classmethod
    def create(cls, obj):
        if isinstance(obj, dict):
            return cls.from_dict(obj)
        if isinstance(obj, str):
            return cls.from_json(obj)
        if isinstance(obj, list):
            return [cls.create(item) for item in obj]
        return None


@dataclass
class Profile(BaseModel):
    """ Example Profile
    {
        "avatar_hash": "ge3b51ca72de",
        "status_text": "Print is dead",
        "status_emoji": ":books:",
        "real_name": "Egon Spengler",
        "display_name": "spengler",
        "real_name_normalized": "Egon Spengler",
        "display_name_normalized": "spengler",
        "email": "spengler@ghostbusters.example.com",
        "image_original": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "image_24": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "image_32": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "image_48": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "image_72": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "image_192": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "image_512": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "team": "T012AB3C4"
    }
    """
    real_name: str
    display_name: str
    real_name_normalized: str
    display_name_normalized: str
    team: str


@dataclass
class User(BaseModel):
    """ Example API User:
    {
        "id": "W012A3CDE",
        "team_id": "T012AB3C4",
        "name": "spengler",
        "deleted": false,
        "color": "9f69e7",
        "real_name": "Egon Spengler",
        "tz": "America/Los_Angeles",
        "tz_label": "Pacific Daylight Time",
        "tz_offset": -25200,
        "profile": {
            "avatar_hash": "ge3b51ca72de",
            "status_text": "Print is dead",
            "status_emoji": ":books:",
            "real_name": "Egon Spengler",
            "display_name": "spengler",
            "real_name_normalized": "Egon Spengler",
            "display_name_normalized": "spengler",
            "email": "spengler@ghostbusters.example.com",
            "image_original": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_24": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_32": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_48": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_72": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_192": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_512": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "team": "T012AB3C4"
        },
        "is_admin": true,
        "is_owner": false,
        "is_primary_owner": false,
        "is_restricted": false,
        "is_ultra_restricted": false,
        "is_bot": false,
        "updated": 1502138686,
        "is_app_user": false,
        "has_2fa": false
    }
    """
    id: str
    name: str
    real_name: str
    team_id: str
    profile: Profile

    def get_short_name(self):
        if self.profile is not None:
            name = self.profile.display_name_normalized
            if name is not None and name != '':
                return name
            name = self.profile.real_name_normalized
            if name is not None and name != '':
                return name
        if self.name is not None and self.name != '':
            return self.name
        return 'unknown'


@dataclass
class Conversation(BaseModel):
    id: str
    name: Optional[str] = None
    is_channel: bool = False
    is_group: bool = False
    is_private: bool = False
    is_im: bool = False


@dataclass
class Team(BaseModel):
    id: str
    name: str
    domain: str


@dataclass
class Message(BaseModel):
    user: str
    text: str
    ts: str


@dataclass
class RateLimitedEvent(DataClassJsonMixin):
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


@dataclass
class Event(BaseModel):
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
        subtype = self.event.get('subtype', None)
        if event_type == 'reaction_added' or event_type == 'reaction_removed':
            return ReactionAdded.from_dict(self.event)
        elif event_type == 'message' and subtype != 'message_changed':
            return MessageSent.from_dict(self.event)

        return None


@dataclass
class ReactionItem(DataClassJsonMixin):
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


@dataclass
class ReactionAdded(BaseModel):
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


@dataclass
class MessageSent(BaseModel):
    """ Example Event:
    {
        "type": "message",
        "channel": "C024BE91L",
        "user": "U2147483697",
        "text": "Live long and prospect.",
        "ts": "1355517523.000005",
        "event_ts": "1355517523.000005",
        "channel_type": "channel"
    }
    """
    channel: str
    user: str
    text: str
    ts: str
    event_ts: str
    channel_type: str
