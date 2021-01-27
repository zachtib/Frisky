from django.db import models


class StonkGame(models.Model):
    channel_name = models.CharField(max_length=200)
    starting_balance = models.DecimalField(max_digits=19, decimal_places=2)

    def __str__(self):
        return f'StonkGame in #{self.channel_name}'


class StonkPlayer(models.Model):
    game = models.ForeignKey(StonkGame, related_name='players', on_delete=models.CASCADE)
    username = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=19, decimal_places=2)

    def __str__(self):
        return f'StonkPlayer @{self.username} in #{self.game.channel_name} with ${self.balance}'


class StonkHolding(models.Model):
    player = models.ForeignKey(StonkPlayer, related_name='holdings', on_delete=models.CASCADE)
    symbol = models.CharField(max_length=5)
    amount = models.IntegerField()

    def __str__(self):
        return f'{self.amount} shares of {self.symbol} owned by @{self.player.username}'
