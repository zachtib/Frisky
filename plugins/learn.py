from typing import Tuple, Optional

from frisky.events import ReactionEvent, MessageEvent
from frisky.plugin import FriskyPlugin
from learns.queries import add_learn, get_random_learn, get_learn_indexed, get_learned_label_counts


class LearnPlugin(FriskyPlugin):

    @classmethod
    def help_text(cls) -> Optional[str]:
        return '\n'.join([
            '*Command Usage*',
            ' • `?learn <label> <index>` - get a value for `<label>`, if `<index>` is not sent one is chosen at random',
            ' • `?<label> <index>` - short hand for the `?learn <label> ...`',
            ' • `?learn <label> <value>` - add `<value>` to `<label>`',
            ' • `?learn_count - show the counts of learned phrases by label (alias: `?lc`)',
            '*Emoji*',
            ' • Tag a user message with :brain: for frisky to learn a quote from that user'
        ])

    @classmethod
    def register_emoji(cls) -> Tuple:
        return 'brain',

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'learn', 'lc', 'learn_count', '*'

    def handle_reaction(self, reaction: ReactionEvent) -> Optional[str]:
        if reaction.emoji == 'brain':
            if add_learn(reaction.message.username, reaction.message.text):
                return f'Okay, learned {reaction.message.username}'

    def handle_message(self, message: MessageEvent) -> Optional[str]:
        if message.command in ['learn_count', 'lc']:
            return self.learn_count()
        else:
            return self.learn(message)

    @staticmethod
    def learn_count() -> Optional[str]:
        return '*Counts*\n'+('\n'.join([f' • {lc["label"]}: {lc["total"]}' for lc in get_learned_label_counts()]))

    @staticmethod
    def learn(message: MessageEvent) -> Optional[str]:
        if message.command != 'learn':
            message.args = (message.command,) + message.args
        if len(message.args) == 0:
            return
        label = message.args[0]
        if len(message.args) == 1:
            # Return a random learn
            # ?learn foobar
            try:
                return get_random_learn(label).content
            except:
                pass
            try:
                return get_random_learn('error').content
            except:
                return 'I got nothing, boss'
        elif len(message.args) == 2:
            # First, see if it's an int index
            # ?learn foobar 2
            try:
                index = int(message.args[1])
                return get_learn_indexed(label, index).content
            except ValueError:
                if message.command == 'learn':
                    if message.args[1].startswith('?'):
                        return "DON'T HURT ME AGAIN"
                    if add_learn(label, message.args[1]):
                        return f'Okay, learned {message.args[0]}'
            except IndexError:
                return 'NO SUCH THING'
        elif len(message.args) > 2:
            new_learn = ' '.join(message.args[1:])
            if new_learn.startswith('?'):
                return "DON'T HURT ME AGAIN"
            if add_learn(label, new_learn):
                return f'Okay, learned {message.args[0]}'
