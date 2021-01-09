from typing import Tuple, Optional, List

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin, PluginRepositoryMixin
from frisky.responses import FriskyError, FriskyResponse
from frisky.util import quotesplit


class PipePlugin(FriskyPlugin, PluginRepositoryMixin):

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'pipe', '|'

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        """
        example usage: `?pipe votes thing | learn thing | ping`
        :param message:
        :return:
        """
        if message.command not in ('pipe', '|'):
            return
        built_args = []
        for arg in message.args:
            arg = arg.strip()
            if ' ' in arg:
                built_args.append(f'"{arg}"')
            else:
                built_args.append(arg)
        raw_text = ' '.join(built_args)
        split_commands = raw_text.split('|')

        previous_result: Optional[str] = None
        for item in split_commands:
            item = item.strip(' ')
            if previous_result:
                item = ' '.join([item, f'"{previous_result}"'])
            split_item = quotesplit(item.strip(' '))
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
                plugins = self.get_generic_handlers()
                event = self.convert_message_to_generic(event)
                responses = [plugin.handle_message(event) for plugin in plugins]
                filtered_responses = [r for r in responses if r is not None and not isinstance(r, FriskyError)]
                if len(filtered_responses) > 1:
                    return FriskyError(f'Too many plugins returned a response for {command}')
                elif len(filtered_responses) == 0:
                    return FriskyError(f'No plugins returned a response for {command}')
                previous_result = filtered_responses[0]
            else:
                previous_result = plugin.handle_message(event)
        return previous_result
