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
        return ()

    @classmethod
    def register_commands(cls) -> Tuple:
        return ()

    @classmethod
    def help_text(cls) -> Optional[str]:
        return None

    def cacheify(self, fn, *args):
        key = ':'.join([fn.__name__] + [str(x) for x in args])
        return self.cache.get_or_set(key, lambda: fn(*args))

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        pass

    def handle_reaction(self, reaction: ReactionEvent) -> FriskyResponse:
        pass


class PluginRepositoryMixin(object):
    loaded_plugins: Dict[str, FriskyPlugin]

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
