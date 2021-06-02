import logging
from dataclasses import dataclass
from typing import Optional

from slack.errors import UnsupportedSlackEventTypeError

logger = logging.getLogger(__name__)


@dataclass
class EventProperties(object):
    event_id: str
    team_id: str
    channel_id: str
    user_id: str
    event_type: str
    event_subtype: Optional[str] = None


class SlackEventProcessor(object):
    def __init__(self):
        pass

    def parse_event_properties(self, payload: dict) -> EventProperties:
        event = payload['event']
        event_type = event['type']
        if event_type == 'message':
            subtype = event.get('subtype')
            if subtype is None:
                """
                From the documentation for message_replied:

                Bug alert! This event is missing the subtype field when dispatched over the Events API.
                Until it is fixed, examine message events' thread_ts value. When present, it's a reply. 
                To be doubly sure, compare a thread_ts to the top-level ts value, when they differ the 
                latter is a reply to the former.
                """
                message = event.get('message', {})
                thread_ts = message.get('thread_ts')
                if thread_ts is not None:
                    assert event['ts'] != thread_ts
                    subtype = 'message_replied'
                else:
                    subtype = 'message_sent'

            if subtype == 'message_sent':
                return EventProperties(
                    event_id=payload['event_id'],
                    event_type=event_type,
                    event_subtype=subtype,
                    team_id=payload['team_id'],
                    channel_id=event['channel'],
                    user_id=event['user']
                )
            elif subtype == 'message_changed':
                return EventProperties(
                    event_id=payload['event_id'],
                    event_type=event_type,
                    event_subtype=subtype,
                    team_id=payload['team_id'],
                    channel_id=event['channel'],
                    user_id=event['message']['user']
                )
            elif subtype == 'message_deleted':
                return EventProperties(
                    event_id=payload['event_id'],
                    event_type=event_type,
                    event_subtype=subtype,
                    team_id=payload['team_id'],
                    channel_id=event['channel'],
                    user_id=event['previous_message']['user']
                )
            elif subtype == 'message_replied':
                return EventProperties(
                    event_id=payload['event_id'],
                    event_type=event_type,
                    event_subtype=subtype,
                    team_id=payload['team_id'],
                    channel_id=event['channel'],
                    user_id=event['message']['user']
                )
            else:
                raise UnsupportedSlackEventTypeError(event_type=f'message.{subtype}')
        elif event_type in ('reaction_added', 'reaction_removed'):
            reacted_item = event['item']
            return EventProperties(
                    event_id=payload['event_id'],
                    event_type=event_type,
                    event_subtype=None,
                    team_id=payload['team_id'],
                    channel_id=reacted_item['channel'],
                    user_id=event['user']
            )
        else:
            # This is an event type we don't handle (yet)
            raise UnsupportedSlackEventTypeError(event_type)
