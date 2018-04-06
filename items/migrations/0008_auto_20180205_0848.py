# Generated by Django 2.0.1 on 2018-02-05 08:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0007_auto_20180205_0826'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogueSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Name of the source')),
                ('description', models.TextField(verbose_name='Description of the source')),
            ],
        ),
        migrations.AddField(
            model_name='catalogue',
            name='source',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='items.CatalogueSource'),
        ),
    ]