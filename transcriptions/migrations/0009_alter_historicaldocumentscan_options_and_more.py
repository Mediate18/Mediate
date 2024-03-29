# Generated by Django 4.1.2 on 2022-11-07 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("transcriptions", "0008_auto_20220705_1028"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="historicaldocumentscan",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical document scan",
                "verbose_name_plural": "historical document scans",
            },
        ),
        migrations.AlterModelOptions(
            name="historicalsourcematerial",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical source material",
                "verbose_name_plural": "historical source materials",
            },
        ),
        migrations.AlterModelOptions(
            name="historicaltranscription",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical shelf mark of transcribed copy",
                "verbose_name_plural": "historical shelf mark of transcribed copies",
            },
        ),
        migrations.AlterField(
            model_name="historicaldocumentscan",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="historicalsourcematerial",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="historicaltranscription",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
    ]
