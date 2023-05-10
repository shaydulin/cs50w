# Generated by Django 4.1.6 on 2023-04-14 20:40

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_user_follower'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='like',
        ),
        migrations.AddField(
            model_name='post',
            name='likes',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]