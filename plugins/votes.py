from datetime import date
from typing import Optional, Tuple

from frisky.events import ReactionEvent, MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse
from votes.models import Vote


class VotesPlugin(FriskyPlugin):

    commands = ['votes', 'upvote', 'downvote', '++', '--', 'leaderboard']
    command_aliases = {
        '++': 'upvote',
        '--': 'downvote',
    }
    reactions = ['upvote', 'downvote']
    help = 'Usage: `?votes <thing>` to get the vote count for `thing`, :upvote: and :downvote: to vote'

    def __get_festive_score_unit(self) -> Tuple[str, str]:
        today = date.today()
        if today.month == 10:
            return 'halloween candy', 'halloween candies',
        if today.month == 12:
            return 'candy cane', 'candy canes'
        return 'friskypoint', 'friskypoints'

    def __format_score(self, count):
        units = self.__get_festive_score_unit()
        if count == 1:
            return f'1 {units[0]}'
        else:
            return f'{count} {units[1]}'

    def __do_upvote(self, user, thing, silent=False) -> Optional[str]:
        if user == thing:
            if not silent:
                return f'Nice try, {user}, you can\'t upvote yourself'
        else:
            record = Vote.objects.upvote(thing)
            if not silent:
                return f'{user} upvoted {thing}! {thing} has {self.__format_score(record.votes)}'

    def __do_downvote(self, user, thing, silent=False) -> Optional[str]:
        if user == thing:
            record = Vote.objects.downvote(thing)
            if not silent:
                return f'You CAN however, downvote yourself. You have {self.__format_score(record.votes)}. Bwahaha.'
        else:
            record = Vote.objects.downvote(thing)
            if not silent:
                return f'{user} downvoted {thing}! {thing} has {self.__format_score(record.votes)}'

    def command_upvote(self, message: MessageEvent) -> FriskyResponse:
        if len(message.args) == 1:
            return self.__do_upvote(message.username, message.args[0])

    def command_downvote(self, message: MessageEvent) -> FriskyResponse:
        if len(message.args) == 1:
            return self.__do_downvote(message.username, message.args[0])

    def command_leaderboard(self, message: MessageEvent) -> FriskyResponse:
        votes = Vote.objects.order_by('-votes')[:10]
        return '\n'.join([f'{vote.label}: {vote.votes}' for vote in votes])

    def command_votes(self, message: MessageEvent) -> FriskyResponse:
        response = []
        for arg in message.args:
            record = Vote.objects.get_record(arg)
            response.append(f'{record.label} has {self.__format_score(record.votes)}')
        return '\n'.join(response)

    def reaction_upvote(self, reaction: ReactionEvent) -> FriskyResponse:
        if reaction.added:
            return self.__do_upvote(reaction.username, reaction.message.username)
        else:
            return self.__do_downvote(reaction.username, reaction.message.username, silent=True)

    def reaction_downvote(self, reaction: ReactionEvent) -> FriskyResponse:
        if reaction.added:
            return self.__do_downvote(reaction.username, reaction.message.username)
        else:
            return self.__do_upvote(reaction.username, reaction.message.username, silent=True)
