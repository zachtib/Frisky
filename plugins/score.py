from typing import Tuple, Dict, Optional

from frisky.events import MessageEvent
from frisky.plugin import FriskyPlugin
from frisky.responses import FriskyResponse
from scores.models import Game


class ScorePlugin(FriskyPlugin):
    NEW_GAME = 'newgame'
    GAIN = 'gain'
    LOSE = 'lose'
    SCORE = 'score'

    @classmethod
    def help_text(cls) -> Optional[str]:
        return f'`?{cls.NEW_GAME} <user1>, <user2> ... <starting_score>` to begin, ' + \
               f'`?{cls.GAIN} <num>` and `?{cls.LOSE} <num>` to alter scores, and ' + \
               f'`?{cls.SCORE}` to view'

    @classmethod
    def register_commands(cls) -> Tuple:
        return cls.NEW_GAME, cls.GAIN, cls.LOSE, cls.SCORE

    @staticmethod
    def format_scores(scores: Dict) -> str:
        return ', '.join([f'{k}: {v}' for (k, v) in scores.items()])

    def handle_message(self, message: MessageEvent) -> FriskyResponse:
        if message.command == self.NEW_GAME:
            players = list(message.args)
            starting_score = players.pop()
            Game.objects.create_named(message.channel_name, starting_score, players)
            return 'Game started'
        game = Game.objects.get_named(message.channel_name)
        if game is None:
            return 'No active game here'
        if message.command == self.SCORE:
            return self.format_scores(game.get_all_scores())

        if len(message.args) == 0:
            players = [message.username]
            delta = 1
        elif len(message.args) == 1:
            players = [message.username]
            delta = int(message.args[0])
        else:
            players = list(message.args)
            delta = int(players.pop())

        if message.command == self.LOSE:
            delta *= -1

        for name in players:
            game.alter_score(name, delta)

        return self.format_scores(game.get_all_scores())
