from celery import shared_task


@shared_task
def process_event(self, event):
    pass
