import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from .models import *


# Person table
class PersonTable(tables.Table):
    edit = tables.LinkColumn('person_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Person
        attrs = {'class': 'table table-sortable'}


# PersonPersonRelation table
class PersonPersonRelationTable(tables.Table):
    edit = tables.LinkColumn('personpersonrelation_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = PersonPersonRelation
        attrs = {'class': 'table table-sortable'}


# PersonPersonRelationType table
class PersonPersonRelationTypeTable(tables.Table):
    edit = tables.LinkColumn('personpersonrelationtype_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = PersonPersonRelationType
        attrs = {'class': 'table table-sortable'}


# PersonProfession table
class PersonProfessionTable(tables.Table):
    edit = tables.LinkColumn('personprofession_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = PersonProfession
        attrs = {'class': 'table table-sortable'}


# Place table
class PlaceTable(tables.Table):
    edit = tables.LinkColumn('place_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Place
        attrs = {'class': 'table table-sortable'}


# Profession table
class ProfessionTable(tables.Table):
    edit = tables.LinkColumn('profession_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Profession
        attrs = {'class': 'table table-sortable'}


# Religion table
class ReligionTable(tables.Table):
    edit = tables.LinkColumn('religion_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Religion
        attrs = {'class': 'table table-sortable'}


# ReligiousAffiliation table
class ReligiousAffiliationTable(tables.Table):
    edit = tables.LinkColumn('religiousaffiliation_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = ReligiousAffiliation
        attrs = {'class': 'table table-sortable'}


# Residence table
class ResidenceTable(tables.Table):
    edit = tables.LinkColumn('residence_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Residence
        attrs = {'class': 'table table-sortable'}


