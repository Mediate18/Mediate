# Generated by Django 2.2.28 on 2022-05-30 09:50

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('catalogues', '0028_auto_20220414_1001'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogueCollectionRelation',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('catalogue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogues.Catalogue')),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogues.Collection')),
            ],
        ),
        migrations.AddField(
            model_name='collection',
            name='catalogue_m2m',
            field=models.ManyToManyField(related_name='collection_m2m', through='catalogues.CatalogueCollectionRelation', to='catalogues.Catalogue'),
        ),
    ]
