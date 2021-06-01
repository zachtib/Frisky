# Generated by Django 3.2.2 on 2021-06-01 17:03

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('frisky', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('channel_id', models.CharField(max_length=20)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('is_channel', models.BooleanField()),
                ('is_group', models.BooleanField()),
                ('is_private', models.BooleanField()),
                ('is_im', models.BooleanField()),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channels', to='frisky.workspace')),
            ],
            options={
                'unique_together': {('workspace_id', 'channel_id')},
            },
        ),
    ]