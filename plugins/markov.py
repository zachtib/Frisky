import markovify

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from learns.queries import get_all_learns_for_label, get_all_learns


class MarkovPlugin(FriskyPlugin):
    commands = ['markov']

    command_aliases = {
        'm': 'markov',
    }

    def command_markov(self, message: MessageEvent):
        if len(message.args) > 0:
            quotes = []
            for item in message.args:
                query = get_all_learns_for_label(item)
                quotes.extend(list(query.values_list('content', flat=True)))
        else:
            query = get_all_learns()
            quotes = list(query.values_list('content', flat=True))
        text = '\n'.join(quotes)

        text_model = markovify.NewlineText(text, well_formed=False)

        sentence = text_model.make_sentence(tries=100)
        return sentence
