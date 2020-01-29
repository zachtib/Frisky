from votes.queries import get_votes_record, upvote, downvote


def help_text(*args, **kwargs):
    return 'Usage: `?votes <thing>` to get the vote count for `thing`, :upvote: and :downvote: to vote'


def handle_reaction(reaction, reacting_user, commenting_user, comment, added):
    if reaction == 'upvote':
        if reacting_user == commenting_user and added:
            return f'Nice try, {reacting_user}, you can\'t upvote yourself'
        elif added:
            record = upvote(commenting_user)
            return f'{reacting_user} upvoted {commenting_user}! {commenting_user} has {record.votes} friskypoints.'
        else:
            downvote(commenting_user)
    elif reaction == 'downvote':
        if reacting_user == commenting_user and added:
            record = downvote(commenting_user)
            return f'You CAN however, downvote yourself. You have {record.votes} friskypoints'
        elif added:
            record = downvote(commenting_user)
            return f'{reacting_user} downvoted {commenting_user}! {commenting_user} has {record.votes} friskypoints.'
        else:
            upvote(commenting_user)


def handle_message(*args, **kwargs):
    response = []
    for arg in args:
        record = get_votes_record(arg)
        response.append(f'{record.label} has {record.votes} {"vote" if record.votes == 1 else "votes"}')
    return '\n'.join(response)
