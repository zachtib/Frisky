from django.db import models


class Learn(models.Model):
    label = models.CharField(max_length=50, db_index=True)
    content = models.CharField(max_length=2000)

    def __str__(self):
        return f'{self.label}: "{self.content}"'
