from django.db import models

from frisky.models import Channel


class BetterStonkGame(models.Model):
    channel = models.ForeignKey(Channel, null=True, on_delete=models.SET_NULL)
    starting_balnance = models.DecimalField(max_digits=19, decimal_places=4)