from typing import Optional

from frisky.events import ReactionEvent, MessageEvent
from frisky.plugin import FriskyPlugin
from learns.models import Learn


class LearnPlugin(FriskyPlugin):
    help = '\n'.join([
        '*Command Usage*',
        ' • `?learn <label> <index>` - get a value for `<label>`, if `<index>` is not sent one is chosen at random',
        ' • `?<label> <index>` - short hand for the `?learn <label> ...`',
        ' • `?learn <label> <value>` - add `<value>` to `<label>`',
        ' • `?learn_count` - show the counts of learned phrases by label (alias: `?lc`)',
        ' • `?learn_search <label> <query>` - Search for learns under label that match query (alias: `?ls`)',
        ' • `?learn_search - <query>` - Search for learns that match query (alias: `?ls`)',
        '*Emoji*',
        ' • Tag a user message with :brain: for frisky to learn a quote from that user'
    ])

    reactions = ['brain']

    commands = ['learn', 'lc', 'learn_count', 'learn_search', 'random', '*']

    command_aliases = {
        'lc': 'learn_count',
        'ls': 'learn_search',
        'learnsearch': 'learn_search',
        '*': 'learn'
    }

    def reaction_brain(self, reaction: ReactionEvent) -> Optional[str]:
        if reaction.message.text is not None:
            return self.create_new_learn(reaction.message.username, reaction.message.text)
        return 'This is a learning-free zone!'

    @staticmethod
    def command_learn_count(message: MessageEvent):
        if len(message.args) == 0:
            learn_counts = Learn.objects.label_counts()
            learn_counts = [lc for lc in learn_counts if lc["total"] > 1]
            learn_counts = learn_counts[:10]
        elif len(message.args) == 1:
            counts = Learn.objects.count_for_label(message.args[0])
            if counts is None:
                return None
            return f'Count: {counts["total"]}'
        else:
            learn_counts = []
            for item in message.args:
                counts = Learn.objects.count_for_label(item)
                if counts is not None:
                    learn_counts.append(counts)

        if len(learn_counts) == 0:
            return None

        return '*Learn Counts*\n' + ('\n'.join([f' • {lc["label"]}: {lc["total"]}' for lc in learn_counts]))

    @staticmethod
    def command_random(message: MessageEvent):
        learn = Learn.objects.random()
        if learn:
            return f'{learn.label}: {learn.content}'
        return None

    @staticmethod
    def command_learn_search(message: MessageEvent):
        if len(message.args) == 0:
            return LearnPlugin.help
        if len(message.args) >= 2:
            label = message.args[0]
            if label == '-':
                label = None
            query = ' '.join(message.args[1:])
            learns = Learn.objects.search(label=label, query=query)
            if len(learns) > 0:
                if label is None:
                    return '\n'.join([f'{learn.label}: {learn.content}' for learn in learns])
                return '\n'.join([learn.content for learn in learns])

        query = ' '.join(message.args)
        learns = Learn.objects.search(query)
        return '\n'.join([f'{learn.label}: {learn.content}' for learn in learns])

    @staticmethod
    def get_random_learn_for_label(label: str) -> str:
        try:
            return Learn.objects.random(label).content
        except ValueError:
            pass
        try:
            return Learn.objects.random('error').content
        except ValueError:
            pass
        return 'I got nothing, boss'

    @staticmethod
    def get_indexed_learn_for_label(label, index) -> str:
        try:
            return Learn.objects.for_label_indexed(label, index).content
        except IndexError:
            return 'NO SUCH THING'

    @staticmethod
    def create_new_learn(label: str, content: str) -> Optional[str]:
        if content.startswith('?'):
            return "DON'T HURT ME AGAIN"
        if Learn.objects.add(label, content):
            return f'Okay, learned {label}'
        return None

    def command_learn(self, message: MessageEvent) -> Optional[str]:
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
