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
        return ('votes', 'upvote', 'downvote)

    def handle_message(self, message: MessageEvent) -> Optional[str]:
        if message.command == 'votes':
            response = []
            for arg in message.args:
                record = get_votes_record(arg)
                response.append(f'{record.label} has {record.votes} {"vote" if record.votes == 1 else "votes"}')
            return '\n'.join(response)

    def handle_reaction(self, reaction: ReactionEvent) -> Optional[str]:
        if reaction.emoji == 'upvote':
            if reaction.username == reaction.message.username and reaction.added:
                return f'Nice try, {reaction.username}, you can\'t upvote yourself'
            elif reaction.added:
                record = upvote(reaction.message.username)
                return f'{reaction.username} upvoted {reaction.message.username}! {reaction.message.username} has {record.votes} friskypoints.'
            else:
                downvote(reaction.message.username)
        elif reaction.emoji == 'downvote':
            if reaction.username == reaction.message.username and reaction.added:
                record = downvote(reaction.message.username)
                return f'You CAN however, downvote yourself. You have {record.votes} friskypoints'
            elif reaction.added:
                record = downvote(reaction.message.username)
                return f'{reaction.username} downvoted {reaction.message.username}! {reaction.message.username} has {record.votes} friskypoints.'
            else:
                upvote(reaction.message.username)
