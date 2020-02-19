from django.contrib import admin

from memes.models import MemeAlias


@admin.register(MemeAlias)
class MemeAliasAdmin(admin.ModelAdmin):
    pass
