import importlib
import inspect
import logging
import pkgutil
from typing import Dict, List

from django.conf import settings

from frisky.events import MessageEvent, ReactionEvent
from frisky.plugin import FriskyPlugin

logger = logging.getLogger(__name__)


class PluginLoader(object):
    __loaded_plugins: List[FriskyPlugin]
    __message_handlers: Dict[str, List[FriskyPlugin]]
    __reaction_handlers: Dict[str, List[FriskyPlugin]]

    def __init__(self, modules=('plugins',)) -> None:
        super().__init__()
        self.__loaded_plugins = list()
        self.__message_handlers = dict()
        self.__reaction_handlers = dict()
        self.load_plugins(modules)

    def load_plugins(self, modules) -> None:
        for module in modules:
            module_iterator = pkgutil.iter_modules(importlib.import_module(module).__path__)
            for _, name, _ in module_iterator:
                submodule = importlib.import_module(f'{module}.{name}')
                for item_name, item in inspect.getmembers(submodule):
                    if inspect.isclass(item) and item is not FriskyPlugin and issubclass(item, FriskyPlugin):
                        self.__load_plugin_from_class(item)

    def __load_plugin_from_class(self, cls) -> None:
        try:
            plugin = cls()
            self.__loaded_plugins.append(plugin)
            for command in cls.register_commands():
                handlers = self.__message_handlers.get(command, list())
                handlers.append(plugin)
                self.__message_handlers[command] = handlers
            for reaction in cls.register_emoji():
                handlers = self.__reaction_handlers.get(reaction, list())
                handlers.append(plugin)
                self.__reaction_handlers[reaction] = handlers
        except TypeError as err:
            logger.warning(f'Error instantiating plugin {cls}', exc_info=err)

    def get_plugins_for_command(self, command) -> List[FriskyPlugin]:
        return self.__message_handlers.get(command, list())

    def get_plugins_for_reaction(self, reaction) -> List[FriskyPlugin]:
        return self.__reaction_handlers.get(reaction, list())


def parse_message_string(message):
    if message[0] == '?':
        message = message[1:]
    elif message.startswith(settings.FRISKY_BOT_NAME):
        message = message[len(settings.FRISKY_BOT_NAME):]
    message.strip()
    split = message.split()
    command = split[0]
    arguments = split[1:]
    return command, arguments


def get_plugin(command):
    try:
        plugin = importlib.import_module(f'plugins.{command}')
        for k, v in inspect.getmembers(plugin):
            if inspect.isclass(v) and v is not FriskyPlugin and issubclass(v, FriskyPlugin):
                return v()
        return plugin
    except ModuleNotFoundError as e:
        for _, name, _ in pkgutil.iter_modules(importlib.import_module('plugins').__path__):
            plugin = importlib.import_module(f'plugins.{name}')
            for k, v in inspect.getmembers(plugin):
                if inspect.isclass(v) and v is not FriskyPlugin and issubclass(v, FriskyPlugin):
                    if command in v.register_commands():
                        return v()


def get_plugin_for_reaction(reaction):
    temp = pkgutil.iter_modules(importlib.import_module('plugins').__path__)
    for _, name, _ in temp:
        plugin = importlib.import_module(f'plugins.{name}')
        members = inspect.getmembers(plugin)
        for k, v in members:
            if inspect.isclass(v) and v is not FriskyPlugin and issubclass(v, FriskyPlugin):
                if reaction in v.register_emoji():
                    return v()


def get_reply_from_plugin(message, sender, channel):
    command, arguments = parse_message_string(message)
    plugin = get_plugin(command)
    if plugin is not None:
        if isinstance(plugin, FriskyPlugin):
            return plugin.handle_message(MessageEvent(
                username=sender,
                channel_name=channel,
                text=message,
                command=command,
                args=arguments
            ))
        elif hasattr(plugin, 'handle_message'):
            handler = getattr(plugin, 'handle_message')
            if callable(handler):
                return handler(*arguments, channel=channel, sender=sender)
    else:
        plugin: FriskyPlugin = get_plugin('learn')
        args = [command] + arguments
        return plugin.handle_message(MessageEvent(
            username=sender,
            channel_name=channel,
            text=message,
            command=command,
            args=args
        ))


def get_reply_for_reaction(reaction, reacting_user, commenting_user, comment, added):
    plugin = get_plugin_for_reaction(reaction)
    if plugin is None:
        return
    if isinstance(plugin, FriskyPlugin):
        return plugin.handle_reaction(ReactionEvent(
            emoji=reaction,
            username=reacting_user,
            added=added,
            message=MessageEvent(
                username=commenting_user,
                channel_name='',
                text=comment,
                command='',
                args=tuple(),
            )
        ))
    elif hasattr(plugin, 'handle_reaction'):
        # TODO: This should be dead code now
        handler = getattr(plugin, 'handle_reaction')
        if callable(handler):
            return handler(reaction, reacting_user, commenting_user, comment, added)


def handle_message(channel_name, sender, message, reply_channel) -> None:
    if message[0] != '?' and not message.startswith(settings.FRISKY_BOT_NAME):
        return
    reply = get_reply_from_plugin(message, sender, channel_name)
    if reply is not None:
        reply_channel(reply)


def handle_reaction(reaction, reacting_user, commenting_user, comment, added, reply_channel):
    """

    This function is EXPERIMENTAL. Please don't base your plugins on it at this time

    :param comment:
    :param reaction:
    :param reacting_user:
    :param commenting_user:
    :param added:
    :param reply_channel:
    :return:
    """
    reply = get_reply_for_reaction(reaction, reacting_user, commenting_user, comment, added)
    if reply is not None:
        reply_channel(reply)
