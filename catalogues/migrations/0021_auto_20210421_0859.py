# Generated by Django 2.2.13 on 2021-04-21 08:59

from django.db import migrations


def set_initial_datasets(apps, schema_editor):
    Dataset = apps.get_model('catalogues', 'Dataset')
    Collection = apps.get_model('catalogues', 'Collection')

    # Sandbox dataset
    sandbox = Dataset.objects.create(name='Sandbox')
    Collection.objects.filter(catalogue__year_of_publication__gte=1665, catalogue__year_of_publication__lte=1830)\
        .update(dataset=sandbox)

    # Hebrew dataset
    hebrew = Dataset.objects.create(name='Hebrew')
    Collection.objects.filter(catalogue__short_title__contains='HEB').update(dataset=hebrew)

    # Dump dataset
    dump = Dataset.objects.create(name='Dump')
    Collection.objects.exclude(catalogue__year_of_publication__gte=1665, catalogue__year_of_publication__lte=1830)\
        .exclude(catalogue__short_title__contains='HEB').update(dataset=dump)


class Migration(migrations.Migration):

    dependencies = [
        ('catalogues', '0020_auto_20210421_0858'),
    ]

    operations = [
        migrations.RunPython(set_initial_datasets),
    ]