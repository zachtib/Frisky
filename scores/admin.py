from django.contrib import admin

from scores.models import Score, Game


class ScoreInline(admin.TabularInline):
    model = Score
    fields = ['name', 'value']


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    inlines = [
        ScoreInline
    ]
    fields = ['name']
