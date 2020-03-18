from typing import Tuple

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin, PluginRepositoryMixin
from frisky.responses import FriskyResponse


class HelpPlugin(FriskyPlugin, PluginRepositoryMixin):

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'help', '?'

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        if len(message.args) == 1:
            plugin_name = message.args[0]
            if plugin_name == 'help':
                return 'Usage: `?help` or `?help <plugin_name>`'
            plugin = self.get_plugin_by_name(plugin_name)
            if plugin is None:
                return f'No such plugin: `{plugin_name}`, try `?help` to list installed plugins'
            if (help_text := plugin.help_text()) is None:
                return f'Plugin `{plugin_name}` does not provide help text.'
            return help_text
        plugins = self.get_plugin_names()
        joined_string = ', '.join(plugins)
        return f'Available plugins: {joined_string}'
