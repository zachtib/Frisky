from dataclasses import dataclass

from slack.errors import UnsupportedSlackEventTypeError
from slack.processor import EventProperties


@dataclass
class SlackEvent(object):
    event_id: str
    team_id: str
    channel_id: str
    user_id: str
    event_ts: str


@dataclass
class ReactionAddedEvent(SlackEvent):
    reaction: str
    item_user_id: str
    item_ts: str


@dataclass
class ReactionRemovedEvent(SlackEvent):
    reaction: str
    item_user_id: str
    item_ts: str


@dataclass
class MessageSentEvent(SlackEvent):
    text: str


@dataclass
class MessageChangedEvent(SlackEvent):
    text: str
    edited_user_id: str
    edited_ts: str
    previous_text: str
    previous_user_id: str
    previous_ts: str


@dataclass
class MessageDeletedEvent(SlackEvent):
    deleted_ts: str
    previous_text: str
    previous_user_id: str
    previous_ts: str


@dataclass
class MessageRepliedEvent(SlackEvent):
    user_id: str
    text: str
    thread_ts: str


class SlackEventParser(object):

    def parse_event(self, properties: EventProperties, payload: dict) -> SlackEvent:
        if properties.event_type == 'message':
            if properties.event_subtype == 'message_sent':
                return MessageSentEvent(
                    event_id=properties.event_id,
                    team_id=properties.team_id,
                    channel_id=properties.channel_id,
                    user_id=properties.user_id,
                    event_ts=payload['event_ts'],
                    text=payload['text'],
                )
            elif properties.event_subtype == 'message_changed':
                return MessageChangedEvent(
                    event_id=properties.event_id,
                    team_id=properties.team_id,
                    channel_id=properties.channel_id,
                    user_id=properties.user_id,
                    event_ts=payload['event_ts'],
                    text=payload['message']['text'],
                    edited_user_id=payload['message']['edited']['user'],
                    edited_ts=payload['message']['edited']['ts'],
                    previous_text=payload['previous_message']['text'],
                    previous_user_id=payload['previous_message']['user'],
                    previous_ts=payload['previous_message']['ts']
                )
            elif properties.event_subtype == 'message_deleted':
                return MessageDeletedEvent(
                    event_id=properties.event_id,
                    team_id=properties.team_id,
                    channel_id=properties.channel_id,
                    user_id=properties.user_id,
                    event_ts=payload['event_ts'],
                    deleted_ts=payload['deleted_ts'],
                    previous_text=payload['previous_message']['text'],
                    previous_user_id=payload['previous_message']['user'],
                    previous_ts=payload['previous_message']['ts'],
                )
            elif properties.event_subtype == 'message_replied':
                return MessageRepliedEvent(
                    event_id=properties.event_id,
                    team_id=properties.team_id,
                    channel_id=properties.channel_id,
                    user_id=properties.user_id,
                    event_ts=payload['event_ts'],
                    text=payload['message']['text'],
                    thread_ts=payload['message']['thread_ts'],
                )
            else:
                # This is an event type we don't handle (yet)
                raise UnsupportedSlackEventTypeError(event_type=f'message.{properties.event_subtype}')
        elif properties.event_type == 'reaction_added':
            return ReactionAddedEvent(
                event_id=properties.event_id,
                team_id=properties.team_id,
                channel_id=properties.channel_id,
                user_id=properties.user_id,
                event_ts=payload['event_ts'],
                reaction=payload['reaction'],
                item_user_id=payload['item_user'],
                item_ts=payload['item']['ts'],
            )
        elif properties.event_type == 'reaction_removed':
            return ReactionRemovedEvent(
                event_id=properties.event_id,
                team_id=properties.team_id,
                channel_id=properties.channel_id,
                user_id=properties.user_id,
                event_ts=payload['event_ts'],
                reaction=payload['reaction'],
                item_user_id=payload['item_user'],
                item_ts=payload['item']['ts'],
            )
        else:
            # This is an event type we don't handle (yet)
            raise UnsupportedSlackEventTypeError(properties.event_type)
