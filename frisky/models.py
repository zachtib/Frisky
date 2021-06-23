import logging
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from slack.api.client import SlackApiClient

logger = logging.getLogger(__name__)


class WorkspaceManager(models.Manager):
    def get_or_fetch_by_kind_and_id(self, kind: str, team_id: str) -> 'Workspace':
        try:
            workspace = self.get_queryset().get(kind=kind, team_id=team_id)
            # Check to see how long it has been since this item was updated from the api
            delta: timedelta = timezone.now() - workspace.updated
            if delta < timedelta(days=7):
                # If we've refreshed in the last week, simply return it
                return workspace
            # Otherwise, we're going to be fetching from the api
            if workspace.kind == Workspace.Kind.SLACK:
                slack_client = SlackApiClient(workspace.access_token, enable_emergency_log=False)
                refreshed_workspace = slack_client.get_workspace(workspace.team_id)
                if refreshed_workspace is not None:
                    workspace.domain = refreshed_workspace.domain
                    workspace.name = refreshed_workspace.name
                    workspace.save()
                else:
                    logger.warning(f'Failed to refresh Slack Workspace {workspace.team_id}')
                return workspace
            else:
                raise NotImplementedError(f'Updating is not implemented for Workspace Kind {workspace.kind}')
        except Workspace.DoesNotExist:
            # Workspace does not exist, we need to look up via the api
            pass
        if kind == Workspace.Kind.SLACK:
            if settings.SLACK_ACCESS_TOKEN is not None and settings.SLACK_ACCESS_TOKEN != '':
                slack_client = SlackApiClient(settings.SLACK_ACCESS_TOKEN, enable_emergency_log=False)
                fetched_workspace = slack_client.get_workspace(team_id)
                new_workspace = self.create(
                    kind=Workspace.Kind.SLACK,
                    team_id=team_id,
                    name=fetched_workspace.name,
                    domain=fetched_workspace.domain,
                    access_token=settings.SLACK_ACCESS_TOKEN,
                )
                return new_workspace
            else:
                raise RuntimeError('Cannot create a new Slack Workspace when SLACK_ACCESS_TOKEN is undefined')
        else:
            raise NotImplementedError(f'Fetching is not implemented for Workspace Kind {kind}')


class Workspace(models.Model):
    class Kind(models.TextChoices):
        SLACK = 'SL', 'Slack'
        NONE = 'NO', 'None'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    kind = models.CharField(max_length=2, choices=Kind.choices)
    team_id = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    domain = models.CharField(max_length=100)
    access_token = models.CharField(max_length=100)

    objects = WorkspaceManager()

    def __str__(self):
        return f'{self.get_kind_display()} Workspace {self.name}'

    class Meta:
        unique_together = ('kind', 'team_id')


class MemberManager(models.Manager):
    def get_or_fetch_by_workspace_and_id(self, workspace: Workspace, user_id: str) -> 'Member':
        try:
            member = self.get_queryset().get(workspace=workspace, user_id=user_id)
            # Check to see how long it has been since this item was updated from the api
            delta: timedelta = timezone.now() - member.updated
            if delta < timedelta(days=7):
                # If we've refreshed in the last week, simply return it
                return member
            # Otherwise, we're going to be fetching from the api
            if workspace.kind == Workspace.Kind.SLACK:
                slack_client = SlackApiClient(workspace.access_token, enable_emergency_log=False)
                refreshed_user = slack_client.get_user(member.user_id)
                if refreshed_user is not None:
                    member.name = refreshed_user.get_short_name()
                    member.real_name = refreshed_user.get_real_name()
                    member.save()
                else:
                    logger.warning(f'Failed to refresh Slack User {member.user_id}')
                return member
            else:
                raise NotImplementedError(f'Updating is not implemented for Workspace Kind {workspace.kind}')

        except Member.DoesNotExist:
            # Member does not exist, we need to look up via the api
            pass
        if workspace.kind == Workspace.Kind.SLACK:
            slack_client = SlackApiClient(workspace.access_token, enable_emergency_log=False)
            fetched_user = slack_client.get_user(user_id)
            new_member = self.create(
                workspace=workspace,
                user_id=user_id,
                name=fetched_user.get_short_name(),
                real_name=fetched_user.get_real_name(),
            )
            return new_member
        else:
            raise NotImplementedError(f'Fetching is not implemented for Workspace Kind {workspace.kind}')


class Member(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='members')
    user_id = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    real_name = models.CharField(max_length=100)

    objects = MemberManager()

    def __str__(self):
        return f'{self.name} in {str(self.workspace)}'

    def force_refresh(self):
        workspace = self.workspace
        if workspace.kind == Workspace.Kind.SLACK:
            slack_client = SlackApiClient(workspace.access_token, enable_emergency_log=False)
            fetched_user = slack_client.get_user(self.user_id, skip_cache=True)
            if fetched_user is None:
                return
            display_name = fetched_user.get_short_name()
            real_name = fetched_user.get_real_name()
            should_save = False
            if self.name != display_name:
                self.name = display_name
                should_save = True
            if self.real_name != real_name:
                self.real_name = real_name
                should_save = True
            if should_save:
                self.save()
        else:
            raise NotImplementedError(f'Fetching is not implemented for Workspace Kind {workspace.kind}')

    class Meta:
        unique_together = ('workspace_id', 'user_id')


class ChannelManager(models.Manager):
    def get_or_fetch_by_workspace_and_id(self, workspace: Workspace, channel_id: str) -> 'Channel':
        try:
            channel = self.get(workspace=workspace, channel_id=channel_id)
            delta: timedelta = timezone.now() - channel.updated
            if delta < timedelta(days=7):
                # If we've refreshed in the last week, simply return it
                return channel
            # Otherwise, we're going to be fetching from the api
            if workspace.kind == Workspace.Kind.SLACK:
                slack_client = SlackApiClient(workspace.access_token, enable_emergency_log=False)
                refreshed_channel = slack_client.get_channel(channel.channel_id)
                if refreshed_channel is not None:
                    channel.name = refreshed_channel.name
                    channel.is_channel = refreshed_channel.is_channel
                    channel.is_group = refreshed_channel.is_group
                    channel.is_private = refreshed_channel.is_private
                    channel.is_im = refreshed_channel.is_im
                    channel.save()
                else:
                    logger.warning(f'Failed to refresh Slack Channel {channel.channel_id}')
                return channel
            else:
                raise NotImplementedError(f'Updating is not implemented for Workspace Kind {workspace.kind}')

        except Channel.DoesNotExist:
            # Channel does not exist, we need to look up via the api
            pass
        if workspace.kind == Workspace.Kind.SLACK:
            slack_client = SlackApiClient(workspace.access_token, enable_emergency_log=False)
            fetched_channel = slack_client.get_channel(channel_id)
            new_channel = self.create(
                workspace=workspace,
                channel_id=channel_id,
                name=fetched_channel.name,
                is_channel=fetched_channel.is_channel,
                is_group=fetched_channel.is_group,
                is_private=fetched_channel.is_private,
                is_im=fetched_channel.is_im,
            )
            return new_channel
        else:
            raise NotImplementedError(f'Fetching is not implemented for Workspace Kind {workspace.kind}')


class Channel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='channels')
    channel_id = models.CharField(max_length=20)
    name = models.CharField(max_length=100, null=True, blank=True)
    is_channel = models.BooleanField()
    is_group = models.BooleanField()
    is_private = models.BooleanField()
    is_im = models.BooleanField()

    objects = ChannelManager()

    def __str__(self):
        if self.name is None:
            return f'{self.channel_id} in {str(self.workspace)}'
        return f'#{self.name} in {str(self.workspace)}'

    class Meta:
        unique_together = ('workspace_id', 'channel_id')
