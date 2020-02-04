from typing import Optional, Tuple

import requests
from django.core.cache import cache as default_cache, BaseCache

from frisky.events import MessageEvent, ReactionEvent


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
    def cache(self) -> CacheWrapper:
        if self.__cache_wrapper is None:
            self.__cache_wrapper = FriskyPlugin.CacheWrapper(type(self).__name__, default_cache)
        return self.__cache_wrapper

    @property
    def http(self):
        if self.__http_wrapper is None:
            self.__http_wrapper = FriskyPlugin.HttpWrapper()
        return self.__http_wrapper

    def register_emoji(self) -> Tuple:
        return ()

    def register_commands(self) -> Tuple:
        return ()

    def handle_message(self, message: MessageEvent) -> Optional[str]:
        pass

    def handle_reaction(self, reaction: ReactionEvent) -> Optional[str]:
        pass


class FunctionPlugin(FriskyPlugin):
    def __init__(self, name, handle_message=None, handle_reaction=None, help_text=None):
        super().__init__()
        self.name = name
        self.__handle_message = handle_message
        self.__handle_reaction = handle_reaction
        self.__help_text = help_text

    def register_commands(self) -> Tuple:
        return self.name,

    def handle_message(self, message: MessageEvent) -> Optional[str]:
        return self.__handle_message(*message.tokens)

    def handle_reaction(self, reaction: ReactionEvent) -> Optional[str]:
        return self.__handle_reaction(reaction.emoji,
                                      reaction.username,
                                      reaction.message.username,
                                      reaction.message.text,
                                      reaction.added)


PLUGINS = dict()


def register(cls):
    PLUGINS[cls.__name__] = cls
    return cls


def load_plugins():
    import pkgutil
    result = []
    loader = pkgutil.get_loader('plugin')
    for sub_module in pkgutil.walk_packages([loader.filename]):
        _, name, _ = sub_module
        result.append(name)
