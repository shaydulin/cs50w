# Generated by Django 4.1.6 on 2023-02-13 15:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_alter_listing_watchers_alter_listing_winner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='last_price',
        ),
    ]
