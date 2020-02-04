from typing import Tuple

import requests
from django.core.cache import cache as default_cache, BaseCache


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

    def handle_message(self, message):
        pass

    def handle_reaction(self, reaction):
        pass
