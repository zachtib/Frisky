from typing import Optional, Tuple

from frisky.events import ReactionEvent, MessageEvent
from frisky.plugin import FriskyPlugin
from votes.queries import get_votes_record, upvote, downvote


class VotesPlugin(FriskyPlugin):

    @classmethod
    def help_text(cls) -> Optional[str]:
        return 'Usage: `?votes <thing>` to get the vote count for `thing`, :upvote: and :downvote: to vote'

    @classmethod
    def register_emoji(cls) -> Tuple:
        return 'upvote', 'downvote'

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'votes', 'upvote', 'downvote', '++', '--'

    @staticmethod
    def __format_score(count):
        if count == 1:
            return '1 friskypoint'
        else:
            return f'{count} friskypoints'

    def __do_upvote(self, user, thing, silent=False) -> Optional[str]:
        if user == thing:
            if not silent:
                return f'Nice try, {user}, you can\'t upvote yourself'
        else:
            record = upvote(thing)
            if not silent:
                return f'{user} upvoted {thing}! {thing} has {self.__format_score(record.votes)}'

    def __do_downvote(self, user, thing, silent=False) -> Optional[str]:
        if user == thing:
            record = downvote(thing)
            if user == 'alex' and record.votes == 3:
                record = downvote(thing)
                return f'The daily double! Alex has {self.__format_score(record.votes)}!'
            if not silent:
                return f'You CAN however, downvote yourself. You have {self.__format_score(record.votes)}. Bwahaha.'
        else:
            record = downvote(thing)
            if not silent:
                return f'{user} downvoted {thing}! {thing} has {self.__format_score(record.votes)}'

    def handle_message(self, message: MessageEvent) -> Optional[str]:
        if message.command == 'votes':
            response = []
            for arg in message.args:
                record = get_votes_record(arg)
                response.append(f'{record.label} has {self.__format_score(record.votes)}')
            return '\n'.join(response)
        elif message.command in ('upvote', '++') and len(message.args) == 1:
            return self.__do_upvote(message.username, message.args[0])
        elif message.command in ('downvote', '--') and len(message.args) == 1:
            return self.__do_downvote(message.username, message.args[0])

    def handle_reaction(self, reaction: ReactionEvent) -> Optional[str]:
        if reaction.added:
            if reaction.emoji == 'upvote':
                return self.__do_upvote(reaction.username, reaction.message.username)
            elif reaction.emoji == 'downvote':
                return self.__do_downvote(reaction.username, reaction.message.username)
        else:
            if reaction.emoji == 'upvote':
                return self.__do_downvote(reaction.username, reaction.message.username, silent=True)
            elif reaction.emoji == 'downvote':
                return self.__do_upvote(reaction.username, reaction.message.username, silent=True)
