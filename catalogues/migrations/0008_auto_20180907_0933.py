# Generated by Django 2.0 on 2018-09-07 09:33

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('catalogues', '0007_auto_20180808_1452'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogueCatalogueTypeRelation',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='catalogue',
            name='type',
        ),
        migrations.AddField(
            model_name='cataloguecataloguetyperelation',
            name='catalogue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogues.Catalogue'),
        ),
        migrations.AddField(
            model_name='cataloguecataloguetyperelation',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogues.CatalogueType'),
        ),
        migrations.AlterUniqueTogether(
            name='cataloguecataloguetyperelation',
            unique_together={('catalogue', 'type')},
        ),
    ]
