import importlib
import inspect
import logging
import pkgutil
from typing import Dict, List, Tuple, Callable

from frisky.events import MessageEvent, ReactionEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse
from frisky.util import quotesplit

logger = logging.getLogger(__name__)


class Frisky(object):
    name: str
    prefix: str
    __loaded_plugins: Dict[str, FriskyPlugin]
    __message_handlers: Dict[str, List[FriskyPlugin]]
    __reaction_handlers: Dict[str, List[FriskyPlugin]]

    def __init__(self, name, prefix='?', ignored_channels=tuple(), plugin_modules=('plugins',)) -> None:
        super().__init__()
        self.name = name
        self.prefix = prefix
        self.__loaded_plugins = dict()
        self.__message_handlers = dict()
        self.__reaction_handlers = dict()
        self.ignored_channels = ignored_channels
        if plugin_modules is not None:
            self.load_plugins(plugin_modules)

    def load_plugins(self, modules) -> None:
        for module in modules:
            module_iterator = pkgutil.iter_modules(importlib.import_module(module).__path__)
            for _, name, _ in module_iterator:
                submodule = importlib.import_module(f'{module}.{name}')
                for item_name, item in inspect.getmembers(submodule):
                    if inspect.isclass(item) and item is not FriskyPlugin and issubclass(item, FriskyPlugin):
                        self.__load_plugin_from_class(name, item)

    def __load_plugin_from_class(self, name, cls) -> None:
        try:
            plugin = cls()
            self.__loaded_plugins[name] = plugin
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

    def get_plugins_for_command(self, command: str) -> List[FriskyPlugin]:
        return self.__message_handlers.get(command, list())

    def get_generic_handlers(self) -> List[FriskyPlugin]:
        return self.__message_handlers.get('*', list())

    def get_plugins_for_reaction(self, reaction: str) -> List[FriskyPlugin]:
        return self.__reaction_handlers.get(reaction, list())

    @staticmethod
    def convert_message_to_generic(message: MessageEvent) -> MessageEvent:
        message.args = (message.command,) + message.args
        message.command = '*'
        return message

    def __show_help_text(self, args: Tuple[str], reply_channel: Callable[[str], bool]) -> None:
        if len(args) == 1:
            plugin_name = args[0]
            if plugin_name == 'help':
                reply_channel('Usage: `?help` or `?help <plugin_name>`')
                return
            plugin = self.__loaded_plugins.get(plugin_name, None)
            if plugin is None:
                reply_channel(f'No such plugin: `{plugin_name}`, try `?help` to list installed plugins')
            elif (help_text := plugin.help_text()) is None:
                reply_channel(f'Plugin `{plugin_name}` does not provide help text.')
            else:
                reply_channel(help_text)
        else:
            plugins = self.__loaded_plugins.keys()
            joined_string = ', '.join(plugins)
            reply_channel(f'Available plugins: {joined_string}')

    def handle_message(self, message: MessageEvent, reply_channel: Callable[[FriskyResponse], bool]) -> None:
        if message.channel_name in self.ignored_channels or message.username == self.name:
            return
        message.command, message.args = self.parse_message_string(message.text)
        if message.command in ('help', '?'):
            return self.__show_help_text(message.args, reply_channel)
        elif message.command != '':
            plugins = self.get_plugins_for_command(message.command)
            if len(plugins) == 0:
                # Reformat the message as a generic one
                message = self.convert_message_to_generic(message)
                plugins = self.get_generic_handlers()
            for plugin in plugins:
                reply = plugin.handle_message(message)
                if reply is not None:
                    reply_channel(reply)

    def handle_reaction(self, reaction: ReactionEvent, reply_channel: Callable[[str], bool]) -> None:
        if reaction.message.channel_name in self.ignored_channels:
            return
        for plugin in self.get_plugins_for_reaction(reaction.emoji):
            reply = plugin.handle_reaction(reaction)
            if reply is not None:
                reply_channel(reply)

    def parse_message_string(self, message: str) -> Tuple[str, Tuple[str]]:
        if message is None or len(message) == 0:
            return '', tuple()
        if message.startswith(self.prefix):
            message = message[len(self.prefix):]
        elif message.startswith(f'@{self.name}'):
            message = message[len(self.name) + 1:]
        else:
            return '', tuple()
        message = message.strip()
        tokens = quotesplit(message)
        command = tokens[0]
        args = tuple(tokens[1:])
        return command, args
