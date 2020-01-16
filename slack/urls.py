from django.urls import path, include

from .views import handle_event

urlpatterns = [
    path('events/', handle_event),
]
