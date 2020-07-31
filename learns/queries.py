from random import randint

from django.db.models.aggregates import Count

from learns.models import Learn


def get_learned_label_counts():
    return Learn.objects.all() \
        .values('label') \
        .annotate(total=Count('label')) \
        .order_by('-total')


def get_all_learns():
    return Learn.objects.all()


def get_all_learns_for_label(label):
    return Learn.objects.filter(label__iexact=label)


def get_learn_indexed(label: str, index: int):
    learns = get_all_learns_for_label(label)
    if index < 0:
        # Django QuerySets don't support negative indexing, so we'll convert to a positive
        # index by adding the count() of the returned rows.
        # ie, for a size of 3 and index of -1 -> 3 + -1 = 2, which is the last element.
        count = learns.aggregate(count=Count('id'))['count']
        index += count
    return learns[int(index)]


def get_random_learn():
    all_learns = Learn.objects.all()
    count = all_learns.aggregate(count=Count('id'))['count']
    if count == 0:
        return None
    random_index = randint(0, count - 1)
    return all_learns[random_index]


def get_random_learn_for_label(label):
    learns = get_all_learns_for_label(label)
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


def search_learns(label, query):
    if label is None:
        return Learn.objects.filter(content__icontains=query)
    return Learn.objects.filter(label=label, content__icontains=query)
