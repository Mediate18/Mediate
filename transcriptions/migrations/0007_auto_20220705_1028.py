# Generated by Django 2.2.28 on 2022-07-05 10:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transcriptions', '0006_auto_20220704_0805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentscan',
            name='transcription',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='transcriptions.Transcription'),
        ),
    ]
