from django.urls import path

from .views import random_learn, get_response

urlpatterns = [
    path('response/', get_response),
    path('random/', random_learn)
]
