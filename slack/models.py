from django.db import models


class Workspace(models.Model):
    name = models.CharField(max_length=200)
    slack_id = models.CharField(max_length=20)


class Channel(models.Model):
    name = models.CharField(max_length=200)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    slack_id = models.CharField(max_length=20)
    last_update = models.DateTimeField(auto_now=True)


class User(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slack_id = models.CharField(max_length=20)
    last_update = models.DateTimeField(auto_now=True)


class Message(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.CharField(max_length=20)
    last_update = models.DateTimeField(auto_now=True)
