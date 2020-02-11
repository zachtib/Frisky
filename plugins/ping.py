from typing import Tuple, Optional

from frisky.plugin import FriskyPlugin


class PingPlugin(FriskyPlugin):

    @classmethod
    def register_commands(cls) -> Tuple:
        return 'ping',

    def handle_message(self, message) -> Optional[str]:
        return 'pong'
