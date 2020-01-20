from .models import Vote


def get_votes_record(label):
    label = label.lstrip('@')
    obj, created = Vote.objects.get_or_create(label=label)
    return obj


def upvote(label):
    record = get_votes_record(label)
    record.votes += 1
    record.save()
    return record


def downvote(label):
    record = get_votes_record(label)
    record.votes += 1
    record.save()
    return record
