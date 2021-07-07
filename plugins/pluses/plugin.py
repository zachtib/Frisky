from collections import namedtuple
from datetime import date
from typing import Union, Optional

from frisky.events import ReactionEvent, MessageEvent
from frisky.models import Member, Workspace
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse
from plugins.pluses.models import Pluses

PlusUnit = namedtuple("PlusUnit", ["singular", "plural"])


class PlusesPlugin(FriskyPlugin):

    @classmethod
    def get_units(cls, override_date: date = None) -> PlusUnit:
        today = override_date or date.today()
        if today.month == 10:
            return PlusUnit("halloween candy", "halloween candies")
        if today.month == 12:
            return PlusUnit("candy cane", "candy canes")
        return PlusUnit("plus", "pluses")

    @classmethod
    def format_message(
            cls,
            giver: str,
            receiver: str,
            was_upvote: bool,
            count: int,
            override_date: date = None
    ) -> str:
        units = cls.get_units(override_date)
        unit_display = units.singular if count == 1 else units.plural
        verbed = "upvoted" if was_upvote else "downvoted"
        return f"{giver} {verbed} {receiver}! {receiver} has {count} {unit_display}!"

    @classmethod
    def __pluses_for(cls, workspace: Workspace, item: Union[Member, str]) -> Pluses:
        if isinstance(item, Member):
            pluses, created = Pluses.objects.in_workspace(workspace).get_or_create(member=item, defaults={
                "label": None,
                "score": 0,
            })
        else:
            pluses, created = Pluses.objects.in_workspace(workspace).get_or_create(label=item, defaults={
                "member": None,
                "score": 0,
            })
        return pluses

    @classmethod
    def __alter_score(
            cls,
            giver: Member,
            receiver: Union[Member, str],
            inc: bool,
            workspace: Optional[Workspace] = None,
            quiet: bool = False
    ) -> Optional[str]:

        if isinstance(receiver, Member):
            if receiver.id == giver.id and inc:
                return f"Nice try, {receiver.name}, you can't upvote yourself"
            if workspace is None:
                workspace = receiver.workspace
            receiver_display = receiver.name
        else:
            if workspace is None:
                return None
            receiver_display = receiver

        record = cls.__pluses_for(workspace, receiver)
        if inc:
            record.score = record.score + 1
        else:
            record.score = record.score - 1
        record.save()

        if quiet:
            return None
        return cls.format_message(giver.name, receiver_display, inc, record.score)

    def reaction_upvote_added(self, reaction: ReactionEvent) -> FriskyResponse:
        return self.__alter_score(reaction.user, reaction.message.user, True, reaction.workspace)

    def reaction_upvote_removed(self, reaction: ReactionEvent) -> FriskyResponse:
        return self.__alter_score(reaction.user, reaction.message.user, False, reaction.workspace, quiet=True)

    def reaction_downvote_added(self, reaction: ReactionEvent) -> FriskyResponse:
        return self.__alter_score(reaction.user, reaction.message.user, False, reaction.workspace)

    def reaction_downvote_removed(self, reaction: ReactionEvent) -> FriskyResponse:
        return self.__alter_score(reaction.user, reaction.message.user, False, reaction.workspace, quiet=True)

    def command_upvote(self, message: MessageEvent) -> FriskyResponse:
        pass

    def command_downvote(self, message: MessageEvent) -> FriskyResponse:
        pass

    def command_leaderboard(self, message: MessageEvent) -> FriskyResponse:
        pass

    def command_score(self, message: MessageEvent) -> FriskyResponse:
        pass

