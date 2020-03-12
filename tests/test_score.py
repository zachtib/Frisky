from frisky.test import FriskyTestCase
from scores.models import Game


class ScoreTestCase(FriskyTestCase):

    def test_creation(self):
        game = Game.objects.create_named('testing', 20, ['zach', 'asia'])
        self.assertEqual(len(game.scores.all()), 2)

    def test_scores_dict(self):
        game = Game.objects.create_named('testing', 20, ['zach', 'asia'])
        scores = game.get_all_scores()
        expected = {
            'zach': 20,
            'asia': 20
        }
        self.assertDictEqual(expected, scores)

    def test_altering_score(self):
        game = Game.objects.create_named('testing', 20, ['zach', 'asia'])
        game.alter_score('zach', -2)
        scores = game.get_all_scores()
        expected = {
            'zach': 18,
            'asia': 20
        }
        self.assertDictEqual(expected, scores)

    def test_game_creation_cmd(self):
        self.send_message('?newgame zach asia 20', channel='test')
        game = Game.objects.get_named('test')
        self.assertIsNotNone(game)
        scores = game.get_all_scores()
        expected = {
            'zach': 20,
            'asia': 20
        }
        self.assertDictEqual(expected, scores)

    def test_interaction(self):
        print(self.send_message('?newgame zach asia 20', channel='test', user='zach'))
        print(self.send_message('?gain 2', channel='test', user='zach'))
        print(self.send_message('?lose 4', channel='test', user='zach'))
        print(self.send_message('?lose asia 2', channel='test', user='zach'))
