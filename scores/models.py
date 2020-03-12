from typing import Dict

from django.db import models


class GameManager(models.Manager):

    def delete_all_named(self, name):
        self.filter(name=name).delete()

    def create_named(self, name, starting_score, participants):
        self.delete_all_named(name)
        game = self.create(name=name)
        for entrant in participants:
            game.scores.create(
                name=entrant,
                value=starting_score
            )
        return game

    def get_named(self, name):
        try:
            return self.get(name=name)
        except Game.DoesNotExist:
            return None


class Game(models.Model):
    name = models.CharField(max_length=100)

    objects = GameManager()

    def get_all_scores(self) -> Dict:
        result = {}
        for score in self.scores.all():
            result[score.name] = score.value
        return result

    def alter_score(self, name: str, delta: int):
        score = self.scores.get(name=name)
        score.value += delta
        score.save()


class Score(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='scores')
    name = models.CharField(max_length=50)
    value = models.IntegerField()
