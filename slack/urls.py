from django.urls import path

from .views import SlackEvent

urlpatterns = [
    path('events/', SlackEvent.as_view()),
]
