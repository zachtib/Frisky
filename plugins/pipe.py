from typing import Tuple, Optional

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin, PluginRepositoryMixin


class PipePlugin(FriskyPlugin, PluginRepositoryMixin):

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'pipe',

    def handle_message(self, message: MessageEvent) -> Optional[str]:
        """
        example usage: `?pipe votes thing | learn thing | ping`
        :param message:
        :return:
        """
        if not message.command == 'pipe':
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
            args: Tuple[str] = tuple(split_item[1:])
            plugin = self.get_plugin_for_command(command)
            event = MessageEvent(
                username=message.username,
                channel_name=message.channel_name,
                text=item,
                command=command,
                args=args
            )
            previous_result = plugin.handle_message(event)
        return previous_result
