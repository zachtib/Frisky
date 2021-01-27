from django.contrib import admin
from .models import StonkGame, StonkPlayer, StonkHolding


@admin.register(StonkGame)
class StonkGameAdmin(admin.ModelAdmin):
    pass


class StonkHoldingInline(admin.TabularInline):
    model = StonkHolding
    fields = ['symbol', 'amount']


@admin.register(StonkPlayer)
class StonkPlayerAdmin(admin.ModelAdmin):
    inlines = [
        StonkHoldingInline
    ]
