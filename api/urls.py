from django.urls import path

from .views import random_learn

urlpatterns = [
    path('random/', random_learn)
]
