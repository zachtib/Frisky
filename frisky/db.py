from django.db import models

from frisky.models import Workspace


class WorkspaceScopedQuerySet(models.QuerySet):

    def __init__(self, workspace, model=None, query=None, using=None, hints=None):
        super().__init__(model, query, using, hints)
        self.workspace = workspace

    def in_workspace(self):
        return self.filter(workspace=self.workspace)

    def create(self, **kwargs):
        return super().create(workspace=self.workspace, **kwargs)

    def _clone(self):
        """
        Return a copy of the current QuerySet. A lightweight alternative
        to deepcopy().
        """
        c = self.__class__(self.workspace, model=self.model, query=self.query.chain(), using=self._db,
                           hints=self._hints)
        c._sticky_filter = self._sticky_filter
        c._for_write = self._for_write
        c._prefetch_related_lookups = self._prefetch_related_lookups[:]
        c._known_related_objects = self._known_related_objects
        c._iterable_class = self._iterable_class
        c._fields = self._fields
        return c


class WorkspaceScopingManager(models.Manager):

    def in_workspace(self, workspace: Workspace) -> WorkspaceScopedQuerySet:
        return WorkspaceScopedQuerySet(model=self.model, using=self._db, workspace=workspace).in_workspace()


class FriskyModel(models.Model):
    workspace = models.ForeignKey(Workspace, null=True, on_delete=models.SET_NULL, related_name="+")

    objects = WorkspaceScopingManager()

    class Meta:
        abstract = True
