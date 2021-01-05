from django.db import models


class ApiLearn(models.Model):
    label = models.CharField(max_length=50, db_index=True, unique=True)
    url = models.URLField()
    element = models.CharField(blank=True, null=True, default=None, max_length=200)
