from django.urls import path

from .views import SlackEvent, test_celery

urlpatterns = [
    path('events/', SlackEvent.as_view()),
    path('celery/', test_celery),
]
