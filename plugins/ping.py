from typing import Tuple, Optional

from frisky.plugin import FriskyPlugin


class PingPlugin(FriskyPlugin):

    def register_commands(self) -> Tuple:
        return 'ping',

    def handle_message(self, message) -> Optional[str]:
        return 'pong'
