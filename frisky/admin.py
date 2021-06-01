from django.contrib import admin

from frisky.models import Workspace, Member, Channel


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    pass


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    pass


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    pass
