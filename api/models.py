from django.db import models


class ApiToken(models.Model):
    name = models.CharField(max_length=100)
    jwt = models.CharField(max_length=255, db_index=True)
    revoked = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True, default='')

    def __str__(self):
        return f'ApiToken: {self.name}'
