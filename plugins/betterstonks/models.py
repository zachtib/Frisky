from django.db import models

from frisky.db import FriskyModel
from frisky.models import Channel


class BetterStonkGame(FriskyModel):
    channel = models.ForeignKey(Channel, null=True, on_delete=models.SET_NULL)
    starting_balance = models.DecimalField(max_digits=19, decimal_places=4)
