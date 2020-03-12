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

    def test_checking_score(self):
        Game.objects.create_named('test', 20, ['zach', 'asia'])
        reply = self.send_message('?score', channel='test')
        self.assertEqual('zach: 20, asia: 20', reply)

    def test_interaction(self):
        self.send_message('?newgame zach asia 20', channel='test', user='zach')

        game = Game.objects.get_named('test')
        self.assertIsNotNone(game)

        scores = game.get_all_scores()
        expected = {
            'zach': 20,
            'asia': 20
        }
        self.assertDictEqual(expected, scores)

        self.send_message('?gain 2', channel='test', user='zach')
        scores = game.get_all_scores()
        expected = {
            'zach': 22,
            'asia': 20
        }
        self.assertDictEqual(expected, scores)

        self.send_message('?lose 4', channel='test', user='zach')
        scores = game.get_all_scores()
        expected = {
            'zach': 18,
            'asia': 20
        }
        self.assertDictEqual(expected, scores)

        self.send_message('?lose asia 2', channel='test', user='zach')
        scores = game.get_all_scores()
        expected = {
            'zach': 18,
            'asia': 18
        }
        self.assertDictEqual(expected, scores)

        self.send_message('?gain', channel='test', user='zach')
        scores = game.get_all_scores()
        expected = {
            'zach': 19,
            'asia': 18
        }
        self.assertDictEqual(expected, scores)

    def test_no_game(self):
        game = Game.objects.get_named('test')
        self.assertIsNone(game)

    def test_no_game_cmd(self):
        reply = self.send_message('?score')
        self.assertEqual('No active game here', reply)
