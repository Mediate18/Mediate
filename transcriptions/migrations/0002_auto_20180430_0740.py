# Generated by Django 2.0 on 2018-04-30 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transcriptions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transcription',
            name='date',
            field=models.DateField(auto_now_add=True, verbose_name='Creation date'),
        ),
    ]
