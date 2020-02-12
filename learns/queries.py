from random import randint

from django.db.models.aggregates import Count

from learns.models import Learn


def get_all_learns(label):
    return Learn.objects.filter(label=label)


def get_learn_indexed(label: str, index: int):
    learns = get_all_learns(label)
    if index < 0:
        # Django QuerySets don't support negative indexing, so we'll convert to a positive
        # index by adding the count() of the returned rows.
        # ie, for a size of 3 and index of -1 -> 3 + -1 = 2, which is the last element.
        count = learns.aggregate(count=Count('id'))['count']
        index += count
    return learns[int(index)]


def get_random_learn(label):
    learns = get_all_learns(label)
    count = learns.aggregate(count=Count('id'))['count']
    random_index = randint(0, count - 1)
    return learns[random_index]


def add_learn(label, content) -> bool:
    """

    :param label:
    :param content:
    :return: True if the record was created
    """
    if not Learn.objects.filter(label=label, content=content).exists():
        Learn.objects.create(label=label, content=content)
        return True
    return False
