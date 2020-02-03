from typing import List

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

    def __init__(self) -> None:
        self.__cache_wrapper = None

    @property
    def cache(self) -> CacheWrapper:
        if self.__cache_wrapper is None:
            self.__cache_wrapper = FriskyPlugin.CacheWrapper(type(self).__name__, default_cache)
        return self.__cache_wrapper

    def register_emoji(self) -> List:
        pass

    def register_commands(self):
        pass


class PingPlugin(FriskyPlugin):
    def ping(self, *args, **kwargs):
        return self.cache.get_or_set('ping', 'pong')

    def register_commands(self):
        return {
            'ping': lambda *args, **kwargs: 'pong'
        }
