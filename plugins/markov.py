import markovify

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from learns.models import Learn


class MarkovPlugin(FriskyPlugin):
    commands = ['markov']

    command_aliases = {
        'm': 'markov',
    }

    def command_markov(self, message: MessageEvent):
        if len(message.args) > 0:
            quotes = []
            for item in message.args:
                query = Learn.objects.for_label(item)
                quotes.extend(list(query.values_list('content', flat=True)))
        else:
            query = Learn.objects.all()
            quotes = list(query.values_list('content', flat=True))
        text = '\n'.join(quotes)

        text_model = markovify.NewlineText(text, well_formed=False)

        sentence = text_model.make_sentence(tries=100)
        return sentence
