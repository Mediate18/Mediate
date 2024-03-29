# Generated by Django 4.1.2 on 2022-11-07 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tagme", "0002_auto_20190617_1459"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="historicaltag",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical tag",
                "verbose_name_plural": "historical tags",
            },
        ),
        migrations.AlterModelOptions(
            name="historicaltaggedentity",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical tagged entity",
                "verbose_name_plural": "historical TaggedEntities",
            },
        ),
        migrations.AlterField(
            model_name="historicaltag",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="historicaltag",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicaltaggedentity",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="historicaltaggedentity",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="tag",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="taggedentity",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
