# Generated by Django 4.2.1 on 2023-06-28 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0035_copy_edition_place_to_publicationplace'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalitem',
            name='collection_short_title',
            field=models.CharField(editable=False, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='historicalitem',
            name='collection_year_of_publication',
            field=models.IntegerField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='collection_short_title',
            field=models.CharField(editable=False, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='collection_year_of_publication',
            field=models.IntegerField(editable=False, null=True),
        ),
        migrations.AddIndex(
            model_name='item',
            index=models.Index(fields=['collection_year_of_publication', 'collection_short_title'], name='items_item_collect_ee2d04_idx'),
        ),
    ]