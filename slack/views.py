from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse


def event(request):
    if request.method == 'POST':
        print(request.POST)
    return HttpResponse()
