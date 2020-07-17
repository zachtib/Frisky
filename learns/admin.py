from django.contrib import admin

from .models import Learn


@admin.register(Learn)
class LearnAdmin(admin.ModelAdmin):
    search_fields = ['label', 'content']
