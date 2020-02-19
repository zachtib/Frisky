from typing import List

from django.db import models, IntegrityError


class MemeAliasManager(models.Manager):
    def create_alias(self, alias: str, meme_id: int) -> bool:
        try:
            self.create(alias=alias, meme_id=meme_id)
        except IntegrityError:
            return False
        return True

    def get_id_for_alias(self, alias: str) -> int:
        try:
            return self.get(alias=alias).meme_id
        except MemeAlias.DoesNotExist:
            return -1

    def get_all_aliases(self) -> List[str]:
        return self.values_list('alias', flat=True)


class MemeAlias(models.Model):
    alias = models.CharField(max_length=30, unique=True)
    meme_id = models.IntegerField()

    objects = MemeAliasManager()

    def __str__(self):
        return self.alias
