from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin, FriskyApiPlugin
from frisky.responses import FriskyResponse

from apilearns.models import ApiLearn


class ApiLearnPlugin(FriskyPlugin):
    commands = ['learnapi', 'unlearnapi', '*']

    command_aliases = {
        '*': 'get_api',
    }

    def command_learnapi(self, message: MessageEvent) -> FriskyResponse:
        if len(message.args) == 2:
            label = message.args[0]
            url = message.args[1]
            element = None
        elif len(message.args) == 3:
            label = message.args[0]
            url = message.args[1]
            element = message.args[2]
        else:
            return None
        url = url.removeprefix('<').removesuffix('>')
        ApiLearn.objects.create(label=label, url=url, element=element)
        return f'OK, learned {label}'

    def command_unlearnapi(self, message: MessageEvent) -> FriskyResponse:
        if len(message.args) != 1:
            return
        try:
            ApiLearn.objects.get(label=message.args[0]).delete()
            return f'OK, unlearned {message.args[0]}'
        except ApiLearn.DoesNotExist:
            return None

    def command_get_api(self, message: MessageEvent) -> FriskyResponse:
        try:
            api = ApiLearn.objects.get(label=message.args[0])
            url = api.url
            index = 1
            while len(message.args) > index:
                to_replace = '${' + str(index) + '}'
                url = url.replace(to_replace, message.args[1])
                index = index + 1
        except ApiLearn.DoesNotExist:
            return None
        return FriskyApiPlugin.do_api_call(self.http, url, api.element)
