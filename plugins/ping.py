from typing import Optional

from frisky.plugin import FriskyPlugin


class PingPlugin(FriskyPlugin):
    commands = ['ping']

    def command_ping(self, message) -> Optional[str]:
        return 'pong'
