from random import randint

from django.db.models.aggregates import Count

from learns.models import Learn


def get_all_learns(label):
    return Learn.objects.filter(label=label)


def get_learn_indexed(label, index):
    learns = get_all_learns(label)
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
