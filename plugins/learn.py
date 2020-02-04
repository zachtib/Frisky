from typing import Tuple, Optional

from frisky.events import ReactionEvent, MessageEvent
from frisky.plugin import FriskyPlugin
from learns.queries import add_learn, get_random_learn, get_learn_indexed


class LearnPlugin(FriskyPlugin):

    def register_emoji(self) -> Tuple:
        return 'brain',

    def register_commands(self) -> Tuple:
        return 'learn',

    def handle_reaction(self, reaction: ReactionEvent) -> Optional[str]:
        if reaction.emoji == 'brain':
            if add_learn(reaction.message.username, reaction.message.text):
                return f'Okay, learned {reaction.message.username}'

    def handle_message(self, message: MessageEvent) -> Optional[str]:
        if len(message.tokens) == 0:
            return
        label = message.tokens[0]
        if len(message.tokens) == 1:
            # Return a random learn
            # ?learn foobar
            try:
                return get_random_learn(label).content
            except:
                return 'I got nothing, boss'
        elif len(message.tokens) == 2:
            # First, see if it's an int index
            # ?learn foobar 2
            try:
                index = int(message.tokens[1])
                return get_learn_indexed(label, index).content
            except ValueError:
                if message.tokens[1].startswith('?'):
                    return "DON'T HURT ME AGAIN"
                if add_learn(label, message.tokens[1]):
                    return f'Okay, learned {message.tokens[0]}'
            except IndexError:
                return 'NO SUCH THING'
        elif len(message.tokens) > 2:
            new_learn = ' '.join(message.tokens[1:])
            if new_learn.startswith('?'):
                return "DON'T HURT ME AGAIN"
            if add_learn(label, new_learn):
                return f'Okay, learned {message.tokens[0]}'
