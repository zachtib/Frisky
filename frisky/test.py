from typing import Optional, Dict

from django.test import TestCase

from frisky.bot import Frisky
from frisky.events import MessageEvent, ReactionEvent
from frisky.models import Workspace, Channel, Member


class FriskyTestCase(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.frisky = Frisky('frisky')
        self.workspace = Workspace.objects.create(kind=Workspace.Kind.NONE, team_id='W00001', name='Testing',
                                                  domain='testing', access_token='super_secret_token')
        self.channels: Dict[str, Channel] = {}
        self.users: Dict[str, Member] = {}

        self.channel = self.get_channel('testing')
        self.member = self.get_user('dummyuser', 'Dummy User')

    def get_channel(self, name: str) -> Channel:
        if name in self.channels:
            return self.channels[name]
        next_int_id = len(self.channels) + 1
        next_id = f'C{next_int_id:05d}'
        channel = Channel.objects.create(workspace=self.workspace, channel_id=next_id, name=name,
                                         is_channel=True, is_group=False, is_private=False, is_im=False)
        self.channels[channel.name] = channel
        return channel

    def get_user(self, name: str, override_real_name: Optional[str] = None) -> Member:
        if name in self.users:
            return self.users[name]
        real_name = override_real_name or name.capitalize()
        next_int_id = len(self.users) + 1
        next_id = f'U{next_int_id:05d}'
        user = Member.objects.create(workspace=self.workspace, user_id=next_id, name=name, real_name=real_name)
        self.users[user.name] = user
        return user

    def create_user_dict(self) -> Dict[str, Member]:
        return {user.user_id: user for user in self.users.values()}

    def construct_message_event(self, message_text: str, override_user: Optional[Member] = None,
                                override_channel: Optional[Channel] = None) -> MessageEvent:
        user = override_user or self.member
        channel = override_channel or self.channel

        return MessageEvent(
            workspace=self.workspace,
            channel=channel,
            user=user,
            users=self.create_user_dict(),
            raw_message=message_text,
            username=user.name,
            channel_name=channel.name,
            text=message_text,
        )

    def send_message(self, message: str, user: Optional[str] = None, channel: Optional[str] = None):
        if user is None:
            message_sender = None
        else:
            message_sender = self.get_user(user)
        if channel is None:
            message_channel = None
        else:
            message_channel = self.get_channel(channel)
        result = None
        event = self.construct_message_event(message, override_user=message_sender, override_channel=message_channel)

        def callback(response: str) -> bool:
            nonlocal result
            result = response
            return True

        self.frisky.handle_message(event, callback)
        return result

    def construct_reaction_event(self, reaction: str, was_added: bool, sending_user: Member, receiving_user: Member,
                                 message_text: str, override_channel: Optional[Channel]) -> ReactionEvent:
        channel = override_channel or self.channel

        return ReactionEvent(
            workspace=self.workspace,
            channel=channel,
            user=sending_user,
            users=self.create_user_dict(),
            emoji=reaction,
            username=sending_user.name,
            added=was_added,
            message=self.construct_message_event(message_text, override_user=receiving_user, override_channel=channel)
        )

    def send_reaction(self, reaction, from_user, to_user, reacted_message='yolo', channel: Optional[str] = None,
                      reaction_removed=False):

        sending_user = self.get_user(from_user)
        receiving_user = self.get_user(to_user)
        if channel is None:
            message_channel = None
        else:
            message_channel = self.get_channel(channel)

        result = None
        event = self.construct_reaction_event(reaction, not reaction_removed, sending_user, receiving_user,
                                              reacted_message, message_channel)

        def callback(response: str) -> bool:
            nonlocal result
            result = response
            return True

        self.frisky.handle_reaction(event, callback)
        return result
