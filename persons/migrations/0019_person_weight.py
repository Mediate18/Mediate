# Generated by Django 4.2.15 on 2025-02-12 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0018_historicalperson_normalised_date_of_birth_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='weight',
            field=models.FloatField(editable=False, null=True),
        ),
    ]
