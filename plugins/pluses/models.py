from django.db import models

from frisky.db import FriskyModel
from frisky.models import Member


class Pluses(FriskyModel):
    member = models.ForeignKey(Member, null=True, on_delete=models.CASCADE, related_name="+")
    label = models.CharField(max_length=250, null=True)
    score = models.IntegerField(default=0)
