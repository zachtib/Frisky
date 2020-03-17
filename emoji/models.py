from django.db import models
from django.db.utils import IntegrityError


class EmojiTokenManager(models.Manager):

    def add_token(self, username: str, token_name: str, token: str) -> bool:
        try:
            self.create(name=token_name, username=username, token=token)
            return True
        except IntegrityError:
            return False

    def list_tokens(self, username: str):
        return self.filter(username=username).all()

    def get_token(self, username: str, token_name: str):
        try:
            return self.get(name=token_name, username=username)
        except EmojiToken.DoesNotExist:
            return None


class EmojiToken(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    token = models.CharField(max_length=200)

    objects = EmojiTokenManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['username', 'name'], name='token_uniqueness')
        ]
