# Generated by Django 2.0 on 2018-10-01 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0009_auto_20180903_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='index_in_lot',
            field=models.IntegerField(default=1, verbose_name='Index in the lot'),
            preserve_default=False,
        ),
    ]
