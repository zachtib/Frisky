from random import randint
from typing import Optional

from django.db import models
from django.db.models import Count


class LearnManager(models.Manager):

    def count_for_label(self, label):
        results = self.get_queryset().filter(label=label) \
            .values('label') \
            .annotate(total=Count('label'))
        if len(results) == 0:
            return None
        return results[0]

    def label_counts(self):
        return self.get_queryset() \
            .values('label') \
            .annotate(total=Count('label')) \
            .order_by('-total')

    def for_label(self, label):
        return self.get_queryset().filter(label__iexact=label)

    def for_label_indexed(self, label: str, index: int):
        learns = self.for_label(label)
        if index < 0:
            # Django QuerySets don't support negative indexing, so we'll convert to a positive
            # index by adding the count() of the returned rows.
            # ie, for a size of 3 and index of -1 -> 3 + -1 = 2, which is the last element.
            count = learns.aggregate(count=Count('id'))['count']
            index += count
        return learns[int(index)]

    def random(self, label=None):
        if label is None:
            all_learns = self.get_queryset().all()
            count = all_learns.aggregate(count=Count('id'))['count']
            if count == 0:
                return None
            random_index = randint(0, count - 1)
            return all_learns[random_index]
        learns = self.for_label(label)
        count = learns.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return learns[random_index]

    def add(self, label: str, content: str) -> bool:
        """

        :param label:
        :param content:
        :return: True if the record was created
        """
        if not self.get_queryset().filter(label=label, content=content).exists():
            self.get_queryset().create(label=label, content=content)
            return True
        return False

    def search(self, query: str, label: Optional[str] = None):
        if label is None:
            return self.get_queryset().filter(content__icontains=query)
        return self.get_queryset().filter(label=label, content__icontains=query)


class Learn(models.Model):
    label = models.CharField(max_length=50, db_index=True)
    content = models.CharField(max_length=2000)

    objects = LearnManager()

    def __str__(self):
        return f'{self.label}: "{self.content}"'
