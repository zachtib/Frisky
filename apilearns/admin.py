from django.contrib import admin

from apilearns.models import ApiLearn


@admin.register(ApiLearn)
class ApiLearnAdmin(admin.ModelAdmin):
    pass
