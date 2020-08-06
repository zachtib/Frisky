import uuid

from django.db import models


class ApiToken(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, db_index=True, editable=False, unique=True)
    name = models.CharField(max_length=100)
    revoked = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True, default='')

    def __str__(self):
        return f'ApiToken: {self.name}'
