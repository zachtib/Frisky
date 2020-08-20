from django.urls import path

from .views import random_learn, get_response, bespoke

urlpatterns = [
    path('response/', get_response),
    path('random/', random_learn),
    path('bespoke/', bespoke),
]
