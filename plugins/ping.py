from typing import Tuple, Generator

from frisky.plugin import FriskyPlugin


class PingPlugin(FriskyPlugin):

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'ping',

    def handle_message(self, message) -> Generator[str, None, None]:
        for _ in message.args:
            yield 'pong'
        yield 'pong'
