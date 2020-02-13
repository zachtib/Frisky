import importlib
import inspect
import logging
import pkgutil
from typing import Dict, List, Tuple, Callable

from frisky.events import MessageEvent, ReactionEvent
from frisky.plugin import FriskyPlugin
from frisky.util import quotesplit

logger = logging.getLogger(__name__)


class Frisky(object):
    name: str
    prefix: str
    __loaded_plugins: List[FriskyPlugin]
    __message_handlers: Dict[str, List[FriskyPlugin]]
    __reaction_handlers: Dict[str, List[FriskyPlugin]]

    def __init__(self, name, prefix='?', ignored_channels=tuple(), plugin_modules=('plugins',)) -> None:
        super().__init__()
        self.name = name
        self.prefix = prefix
        self.__loaded_plugins = list()
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

    def get_plugins_for_command(self, command: str) -> List[FriskyPlugin]:
        result = self.__message_handlers.get(command, list())
        if len(result) == 0:
            result = self.__message_handlers.get('*', list())
        return result

    def get_plugins_for_reaction(self, reaction: str) -> List[FriskyPlugin]:
        return self.__reaction_handlers.get(reaction, list())

    def __show_help_text(self, args: Tuple[str], reply_channel: Callable[[str], bool]) -> None:
        if len(args) == 1:
            command = args[0]
            if command == 'help':
                reply_channel('Usage: `?help` or `?help <plugin_name>`')
                return
            help_texts = []
            for plugin in self.get_plugins_for_command(command):
                help_texts.append(plugin.help_text())
            if len(help_texts) > 0:
                reply_channel('\n'.join(help_texts))
            else:
                reply_channel(f'No help found for {command}')
        else:
            commands = self.__message_handlers.keys()
            joined_string = ', '.join(commands)
            reply_channel(f'Available plugins: {joined_string}')

    def handle_message(self, message: MessageEvent, reply_channel: Callable[[str], bool]) -> None:
        if message.channel_name in self.ignored_channels or message.username == self.name:
            return
        message.command, message.args = self.parse_message_string(message.text)
        if message.command == 'help':
            return self.__show_help_text(message.args, reply_channel)
        elif message.command != '':
            for plugin in self.get_plugins_for_command(message.command):
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
