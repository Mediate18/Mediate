import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from django.utils.html import format_html
from .models import *
from mediate.columns import ActionColumn
from catalogues.models import PersonCatalogueRelation
from items.models import PersonItemRelation
from django.utils.translation import ugettext_lazy as _


# Person table
class PersonTable(tables.Table):
    uuid = ActionColumn('person_detail', 'change_person', 'delete_person', orderable=False)
    catalogues = tables.Column(empty_values=())
    items = tables.Column(verbose_name=_("Items"), empty_values=())
    viaf_id = tables.Column(empty_values=())

    class Meta:
        model = Person
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'short_name',
            'first_names',
            'surname',
            'sex',
            'city_of_birth',
            'date_of_birth',
            'city_of_death',
            'date_of_death',
            'catalogues',
            'items',
            'viaf_id',
            'uuid'
        ]

    def render_catalogues(self, record):
        person_catalogue_relations = PersonCatalogueRelation.objects.filter(person=record)
        relation_groups = []
        for role in set([relation.role for relation in person_catalogue_relations]):
            role_relations = person_catalogue_relations.filter(role=role)
            catalogues = []
            for relation in role_relations:
                catalogue = relation.catalogue
                title = catalogue.short_title
                catalogue_entry = "<a href='{}'>{}</a>".format(reverse_lazy('catalogue_detail', args=[catalogue.pk]), title)
                catalogues.append(catalogue_entry)

            relation_groups.append(
                role.name.capitalize() + ": " + ", ".join(catalogues)
            )
        return format_html("<br/> ".join(relation_groups))

    def render_items(self, record):
        person_item_relations = PersonItemRelation.objects.filter(person=record)
        relation_groups = []
        for role in set([relation.role for relation in person_item_relations]):
            role_relations = person_item_relations.filter(role=role)
            items = []
            for relation in role_relations:
                item = relation.item
                title = item.short_title
                item_entry = "<a href='{}'>{}</a>".format(reverse_lazy('change_item', args=[item.pk]), title)
                items.append(item_entry)

            relation_groups.append(
                role.name.capitalize() + ": " + ", ".join(items)
            )
        return format_html("<br/> ".join(relation_groups))

    def render_viaf_id(self, value):
        if value:
            return format_html('<a target="blank" href="{}">{}</a>'.format(
                value, value
            ))
        else:
            return format_html('-')


# PersonPersonRelation table
class PersonPersonRelationTable(tables.Table):
    edit = tables.LinkColumn('change_personpersonrelation', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = PersonPersonRelation
        attrs = {'class': 'table table-sortable'}


# PersonPersonRelationType table
class PersonPersonRelationTypeTable(tables.Table):
    edit = tables.LinkColumn('change_personpersonrelationtype', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = PersonPersonRelationType
        attrs = {'class': 'table table-sortable'}


# PersonProfession table
class PersonProfessionTable(tables.Table):
    edit = tables.LinkColumn('change_personprofession', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = PersonProfession
        attrs = {'class': 'table table-sortable'}


# Place table
class PlaceTable(tables.Table):
    edit = tables.LinkColumn('change_place', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Place
        attrs = {'class': 'table table-sortable'}


# Profession table
class ProfessionTable(tables.Table):
    edit = tables.LinkColumn('change_profession', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Profession
        attrs = {'class': 'table table-sortable'}


# Religion table
class ReligionTable(tables.Table):
    edit = tables.LinkColumn('change_religion', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Religion
        attrs = {'class': 'table table-sortable'}


# ReligiousAffiliation table
class ReligiousAffiliationTable(tables.Table):
    edit = tables.LinkColumn('change_religiousaffiliation', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = ReligiousAffiliation
        attrs = {'class': 'table table-sortable'}


# Residence table
class ResidenceTable(tables.Table):
    edit = tables.LinkColumn('change_residence', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Residence
        attrs = {'class': 'table table-sortable'}


