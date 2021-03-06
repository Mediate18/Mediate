# Generated by Django 2.0 on 2018-12-03 11:50

from django.db import migrations, models
import django.db.models.deletion


def reverse_references(apps, schema_editor):
    """
    Reverse the foreign key reference from manifestion to item
     to a reference from item to manifestation
    :param apps: 
    :param schema_editor: 
    :return: 
    """
    Item = apps.get_model('items', 'Item')
    Manifestation = apps.get_model('items', 'Manifestation')
    for manifestation in Manifestation.objects.exclude(item__isnull=True):
        item = manifestation.item
        item.manifestation = manifestation
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0012_auto_20181114_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='manifestation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='items', to='items.Manifestation'),
        ),
        migrations.RunPython(reverse_references),
        migrations.RemoveField(
            model_name='manifestation',
            name='item',
        ),
        migrations.AlterField(
            model_name='item',
            name='manifestation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='items.Manifestation'),
        ),
    ]
