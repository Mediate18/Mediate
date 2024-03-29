# Generated by Django 4.2.1 on 2023-06-28 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0036_historicalitem_collection_short_title_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalitem',
            name='dataset_uuid',
            field=models.UUIDField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='dataset_uuid',
            field=models.UUIDField(editable=False, null=True),
        ),
    ]
