from django.db import models


class ApiToken(models.Model):
    jwt = models.CharField(max_length=255, db_index=True)
    revoked = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True, default='')
