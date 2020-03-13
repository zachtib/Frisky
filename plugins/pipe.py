from typing import Tuple, Optional, List

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin, PluginRepositoryMixin


class PipePlugin(FriskyPlugin, PluginRepositoryMixin):

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'pipe', '|'

    def handle_message(self, message: MessageEvent) -> Optional[str]:
        """
        example usage: `?pipe votes thing | learn thing | ping`
        :param message:
        :return:
        """
        if message.command not in ('pipe', '|'):
            return
        raw_text = ' '.join(message.args)
        split_commands = raw_text.split('|')

        previous_result: Optional[str] = None
        for item in split_commands:
            item = item.strip(' ')
            if previous_result:
                item = ' '.join([item, previous_result])
            split_item = item.strip(' ').split(' ')
            command: str = split_item[0]
            args: List[str] = split_item[1:]
            plugin = self.get_plugin_for_command(command)

            event = MessageEvent(
                username=message.username,
                channel_name=message.channel_name,
                text=item,
                command=command,
                args=args
            )
            if plugin is None:
                plugin = self.get_generic_handler()
                if plugin is None:
                    return
                event = self.convert_message_to_generic(event)
            previous_result = plugin.handle_message(event)
        return previous_result
