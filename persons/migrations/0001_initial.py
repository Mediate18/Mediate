# Generated by Django 2.0 on 2018-03-29 13:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=128, null=True, verbose_name='Short name')),
                ('viaf_id', models.CharField(max_length=128, null=True, verbose_name='VIAF ID (https://viaf.org)')),
                ('surname', models.CharField(max_length=128, verbose_name='Surname')),
                ('first_names', models.CharField(max_length=512, verbose_name='First names')),
                ('date_of_birth', models.DateField(verbose_name='Date of birth')),
                ('date_of_death', models.DateField(verbose_name='Date of death')),
                ('sex', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other'), ('UNKNOWN', 'Unknown')], max_length=7, verbose_name='Sex')),
            ],
        ),
        migrations.CreateModel(
            name='PersonPersonRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_year', models.IntegerField(null=True, verbose_name='Start year of interval')),
                ('end_year', models.IntegerField(null=True, verbose_name='End year of inter')),
                ('first_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relations_when_first', to='persons.Person')),
                ('second_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relations_when_second', to='persons.Person')),
            ],
        ),
        migrations.CreateModel(
            name='PersonPersonRelationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Relation type name')),
                ('directed', models.BooleanField(default=False, verbose_name='Directed')),
            ],
        ),
        migrations.CreateModel(
            name='PersonProfession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='persons.Person')),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, null=True, verbose_name='Name of the place')),
                ('cerl_id', models.CharField(max_length=32, null=True, verbose_name='CERL ID of a place')),
            ],
        ),
        migrations.CreateModel(
            name='Profession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Profession name')),
                ('description', models.TextField(blank=True, verbose_name='Profession description')),
            ],
        ),
        migrations.CreateModel(
            name='Religion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Religion name')),
                ('description', models.TextField(verbose_name='Religion description')),
            ],
        ),
        migrations.CreateModel(
            name='ReligiousAffiliation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='persons.Person')),
                ('religion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='persons.Religion')),
            ],
        ),
        migrations.CreateModel(
            name='Residence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_year', models.IntegerField(null=True, verbose_name='Start year of interval')),
                ('end_year', models.IntegerField(null=True, verbose_name='End year of inter')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='persons.Person')),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='persons.Place')),
            ],
        ),
        migrations.AddField(
            model_name='personprofession',
            name='profession',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='persons.Profession'),
        ),
        migrations.AddField(
            model_name='personpersonrelation',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='persons.PersonPersonRelationType'),
        ),
        migrations.AddField(
            model_name='person',
            name='city_of_birth',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='persons_born', to='persons.Place'),
        ),
        migrations.AddField(
            model_name='person',
            name='city_of_death',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='persons_died', to='persons.Place'),
        ),
        migrations.AlterUniqueTogether(
            name='residence',
            unique_together={('person', 'place', 'start_year', 'end_year')},
        ),
        migrations.AlterUniqueTogether(
            name='religiousaffiliation',
            unique_together={('person', 'religion')},
        ),
    ]