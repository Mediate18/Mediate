# Generated by Django 2.0 on 2018-06-27 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogues', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='catalogue',
            options={'ordering': ['year_of_publication', 'short_title']},
        ),
        migrations.AlterModelOptions(
            name='library',
            options={'verbose_name_plural': 'libraries'},
        ),
        migrations.AlterModelOptions(
            name='lot',
            options={'ordering': ['catalogue__year_of_publication', 'catalogue__short_title', 'item_as_listed_in_catalogue']},
        ),
        migrations.AlterField(
            model_name='lot',
            name='number_in_catalogue',
            field=models.CharField(max_length=128, verbose_name='Number in catalogue'),
        ),
    ]