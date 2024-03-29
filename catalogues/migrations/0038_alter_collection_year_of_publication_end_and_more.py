# Generated by Django 4.1.7 on 2023-11-06 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogues', '0037_catalogue_shelf_mark'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='year_of_publication_end',
            field=models.IntegerField(blank=True, null=True, verbose_name='Year of publication: end of range'),
        ),
        migrations.AlterField(
            model_name='historicalcollection',
            name='year_of_publication_end',
            field=models.IntegerField(blank=True, null=True, verbose_name='Year of publication: end of range'),
        ),
    ]
