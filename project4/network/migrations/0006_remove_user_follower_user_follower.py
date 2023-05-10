# Generated by Django 4.1.6 on 2023-04-18 18:09

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0005_remove_user_follower_user_follower'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='follower',
        ),
        migrations.AddField(
            model_name='user',
            name='follower',
            field=models.ManyToManyField(related_name='followers', to=settings.AUTH_USER_MODEL),
        ),
    ]