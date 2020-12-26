from django.db import models


class VoteManager(models.Manager):

    def get_record(self, label):
        label = label.lstrip('@')
        obj, created = self.get_queryset().get_or_create(label=label)
        return obj

    def upvote(self, label):
        record = self.get_record(label)
        record.votes += 1
        record.save()
        return record

    def downvote(self, label):
        record = self.get_record(label)
        record.votes -= 1
        record.save()
        return record


class Vote(models.Model):
    label = models.CharField(max_length=200, db_index=True, unique=True)
    votes = models.IntegerField(default=0)

    objects = VoteManager()

    def __str__(self):
        return f'Votes for {self.label}'
