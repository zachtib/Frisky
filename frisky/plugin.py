from typing import Optional, Tuple, Dict

import requests
from django.core.cache import cache as default_cache, BaseCache

from frisky.events import MessageEvent, ReactionEvent
from frisky.responses import FriskyResponse


class FriskyPlugin(object):
    class CacheWrapper(object):
        def __init__(self, prefix: str, cache: BaseCache):
            self.prefix = prefix
            self.cache = cache

        def __get_key(self, key):
            return f'plugin:{self.prefix}:{key}'

        def get(self, key):
            return self.cache.get(self.__get_key(key))

        def set(self, key, value):
            return self.cache.set(self.__get_key(key), value)

        def get_or_set(self, key, default):
            return self.cache.get_or_set(self.__get_key(key), default)

    class HttpWrapper(object):
        def get(self, *args, **kwargs):
            return requests.get(*args, **kwargs)

        def post(self, *args, **kwargs):
            return requests.post(*args, **kwargs)

    reactions = []
    commands = []
    command_aliases = {}
    help = ''

    def __init__(self) -> None:
        self.__cache_wrapper = None
        self.__http_wrapper = None

    @property
    def cache(self) -> 'CacheWrapper':
        if self.__cache_wrapper is None:
            self.__cache_wrapper = FriskyPlugin.CacheWrapper(type(self).__name__, default_cache)
        return self.__cache_wrapper

    @property
    def http(self):
        if self.__http_wrapper is None:
            self.__http_wrapper = FriskyPlugin.HttpWrapper()
        return self.__http_wrapper

    @classmethod
    def register_emoji(cls) -> Tuple:
        return tuple(cls.reactions)

    @classmethod
    def register_commands(cls) -> Tuple:
        result = cls.commands.copy()
        for key in cls.command_aliases.keys():
            if key not in result:
                result.append(key)
        return tuple(result)

    @classmethod
    def help_text(cls) -> Optional[str]:
        return cls.help

    def cacheify(self, fn, *args):
        key = ':'.join([fn.__name__] + [str(x) for x in args])
        return self.cache.get_or_set(key, lambda: fn(*args))

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        command = message.command
        if command in self.command_aliases.keys():
            command = self.command_aliases[command]
        call = getattr(self, f'command_{command}', None)
        if call is None:
            return None
        return call(message)

    def handle_reaction(self, reaction: ReactionEvent) -> FriskyResponse:
        call = getattr(self, f'reaction_{reaction.emoji}', None)
        if call is None:
            return None
        return call(reaction)


class FriskyApiPlugin(FriskyPlugin):
    url = None
    json_property = None

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        if self.url is None:
            return
        response = self.http.get(self.url)
        if response.status_code != 200:
            return
        if self.json_property is None:
            return response.text
        json = response.json()
        for element in self.json_property.split('.'):
            next = json.get(element, None)
            if next is None:
                return None
            json = next
        return json


class PluginRepositoryMixin(object):
    loaded_plugins: Dict[str, FriskyPlugin]

    def get_plugin_names(self):
        return self.loaded_plugins.keys()

    def get_plugin_by_name(self, name: str) -> Optional[FriskyPlugin]:
        return self.loaded_plugins.get(name, None)

    def get_plugin_for_command(self, command: str) -> Optional[FriskyPlugin]:
        for plugin in self.loaded_plugins.values():
            if command in plugin.register_commands():
                return plugin
        return None

    def get_generic_handler(self) -> Optional[FriskyPlugin]:
        for plugin in self.loaded_plugins.values():
            if '*' in plugin.register_commands():
                return plugin
        return None

    @staticmethod
    def convert_message_to_generic(message: MessageEvent) -> MessageEvent:
        message.args = [message.command] + message.args
        message.command = '*'
        return message
