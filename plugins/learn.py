from typing import Tuple, Optional

from frisky.events import ReactionEvent, MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse
from learns.queries import add_learn, search_learns, get_random_learn_for_label, get_random_learn, get_learn_indexed, \
    get_learned_label_counts


class LearnPlugin(FriskyPlugin):

    @classmethod
    def help_text(cls) -> Optional[str]:
        return '\n'.join([
            '*Command Usage*',
            ' • `?learn <label> <index>` - get a value for `<label>`, if `<index>` is not sent one is chosen at random',
            ' • `?<label> <index>` - short hand for the `?learn <label> ...`',
            ' • `?learn <label> <value>` - add `<value>` to `<label>`',
            ' • `?learn_count` - show the counts of learned phrases by label (alias: `?lc`)',
            '*Emoji*',
            ' • Tag a user message with :brain: for frisky to learn a quote from that user'
        ])

    @classmethod
    def register_emoji(cls) -> Tuple:
        return 'brain',

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'learn', 'lc', 'learn_count', 'learnsearch', 'random', '*'

    def handle_reaction(self, reaction: ReactionEvent) -> Optional[str]:
        if reaction.emoji == 'brain':
            if reaction.message.text is not None:
                return self.create_new_learn(reaction.message.username, reaction.message.text)
            return 'This is a learning-free zone!'

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        if message.command in ['learn_count', 'lc']:
            return self.learn_count()
        elif message.command == 'random':
            return self.random()
        elif message.command == 'learnsearch':
            return self.learn_search(message)
        else:
            return self.learn(message)

    @staticmethod
    def learn_count() -> Optional[str]:
        learn_counts = get_learned_label_counts()
        learn_counts = filter(lambda lc: lc.total > 1, learn_counts)
        learn_counts = learn_counts[:10]

        return '*Counts*\n' + ('\n'.join([f' • {lc["label"]}: {lc["total"]}' for lc in learn_counts]))

    @staticmethod
    def learn_search(message):
        if len(message.args) < 2:
            return
        label = message.args[0]
        query = ' '.join(message.args[1:])
        learns = search_learns(label, query)
        return '\n'.join([learn.content for learn in learns])

    @staticmethod
    def get_random_learn_for_label(label: str) -> str:
        try:
            return get_random_learn_for_label(label).content
        except ValueError:
            pass
        try:
            return get_random_learn_for_label('error').content
        except ValueError:
            pass
        return 'I got nothing, boss'

    @staticmethod
    def get_indexed_learn_for_label(label, index) -> str:
        try:
            return get_learn_indexed(label, index).content
        except IndexError:
            return 'NO SUCH THING'

    @staticmethod
    def create_new_learn(label: str, content: str) -> Optional[str]:
        if content.startswith('?'):
            return "DON'T HURT ME AGAIN"
        if add_learn(label, content):
            return f'Okay, learned {label}'
        return None

    @staticmethod
    def random() -> FriskyResponse:
        learn = get_random_learn()
        if learn:
            return f'{learn.label}: {learn.content}'
        return None

    def learn(self, message: MessageEvent) -> Optional[str]:
        """

        Potential cases:
         * `?learn <label>`                             len(args)=1
         * `?learn <label> <index>`                     len(args)=2     (int)
         * `?learn <label> <value>`                     len(args)=2+
         * `?<label> -> `?* <label>`                    len(args)=1
         * `?<label> <index>` -> `?* <label> <index>`   len(args)=2     (int)

         Index can be omitted, but is always the second element when it is present

        :param message:
        :return:
        """
        num_args = len(message.args)
        if num_args == 0:
            return
        try:
            element = message.args[1]
            index = int(element)
        except (IndexError, ValueError):
            index = None
        label = message.args[0]
        if label.startswith('@'):
            label = label.lstrip('@')

        if num_args == 1:
            # Retrieve a random learn
            return self.get_random_learn_for_label(label)
        elif index is not None:
            # Retrieve an indexed learn
            return self.get_indexed_learn_for_label(label, index)
        elif message.command != '*':
            # Create a learn
            new_learn = ' '.join(message.args[1:])
            return self.create_new_learn(label, new_learn)
        return None
