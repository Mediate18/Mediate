import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from django.utils.html import format_html
from .models import *

from catalogues.models import PersonCatalogueRelation
from mediate.columns import ActionColumn

# Catalogue table
class CatalogueTable(tables.Table):
    uuid = ActionColumn('catalogue_detail', 'change_catalogue', 'delete_catalogue', orderable=False)
    transcription = tables.RelatedLinkColumn()
    collection = tables.RelatedLinkColumn()
    people = tables.Column(empty_values=())
    number_of_lots = tables.Column(empty_values=(), orderable=False)
    number_of_items = tables.Column(empty_values=(), orderable=False)

    class Meta:
        model = Catalogue
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'transcription',
            'short_title',
            'full_title',
            'preface_and_paratexts',
            'year_of_publication',
            'terminus_post_quem',
            'notes',
            'bibliography',
            'collection',
            'people',
            'number_of_lots',
            'number_of_items'
        ]

    def render_full_title(self, record, value):
        return format_html('<a href="{}">{}</a>'.format(reverse_lazy('catalogue_detail', args=[record.pk]),
                                                        value[:50] + "...") if len(value) > 50 else value)

    def render_preface_and_paratexts(self, value):
        return (value[:50] + "...") if len(value) > 50 else value

    def render_people(self, record):
        person_catalogue_relations = PersonCatalogueRelation.objects.filter(catalogue=record)
        relation_groups = []
        for role in set([relation.role for relation in person_catalogue_relations]):
            role_relations = person_catalogue_relations.filter(role=role)
            persons = []
            for relation in role_relations:
                person = relation.person
                name = person.short_name
                viaf = person.viaf_id
                person_entry = "<a href='{}'>{}</a>".format(reverse_lazy('change_person', args=[person.pk]), name)
                if viaf:
                    person_entry += " (<a target='blank' href='{}'>VIAF</a>)".format(viaf)
                persons.append(person_entry)

            relation_groups.append(
                role.name.capitalize() + ": " + ", ".join(persons)
            )
        return format_html("<br/> ".join(relation_groups))

    def render_number_of_lots(self, record):
        return record.num_lots

    def render_number_of_items(self, record):
        return record.num_items


# CatalogueHeldBy table
class CatalogueHeldByTable(tables.Table):
    edit = tables.LinkColumn('change_catalogueheldby', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = CatalogueHeldBy
        attrs = {'class': 'table table-sortable'}


# CatalogueType table
class CatalogueTypeTable(tables.Table):
    edit = tables.LinkColumn('change_cataloguetype', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = CatalogueType
        attrs = {'class': 'table table-sortable'}


# Collection table
class CollectionTable(tables.Table):
    uuid = ActionColumn('collection_detail', 'change_collection', 'delete_collection', orderable=False)

    class Meta:
        model = Collection
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'uuid'
        ]


# CollectionYear table
class CollectionYearTable(tables.Table):
    edit = tables.LinkColumn('change_collectionyear', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = CollectionYear
        attrs = {'class': 'table table-sortable'}


# Library table
class LibraryTable(tables.Table):
    edit = tables.LinkColumn('change_library', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Library
        attrs = {'class': 'table table-sortable'}


# Lot table
class LotTable(tables.Table):
    uuid = ActionColumn('lot_detail', 'change_lot', 'delete_lot', orderable=False)
    catalogue = tables.RelatedLinkColumn()
    category = tables.RelatedLinkColumn()

    class Meta:
        model = Lot
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'catalogue',
            'category',
            'number_in_catalogue',
            'page_in_catalogue',
            'lot_as_listed_in_catalogue',
            'sales_price',
            'uuid'
        ]


# PersonCatalogueRelation table
class PersonCatalogueRelationTable(tables.Table):
    uuid = ActionColumn('personcataloguerelation_detail', 'change_personcataloguerelation',
                        'delete_personcataloguerelation', orderable=False)

    class Meta:
        model = PersonCatalogueRelation
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'person',
            'catalogue',
            'role',
            'uuid'
        ]


# PersonCatalogueRelationRole table
class PersonCatalogueRelationRoleTable(tables.Table):
    edit = tables.LinkColumn('change_personcataloguerelationrole', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = PersonCatalogueRelationRole
        attrs = {'class': 'table table-sortable'}


# PersonCollectionRelation table
class PersonCollectionRelationTable(tables.Table):
    edit = tables.LinkColumn('change_personcollectionrelation', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = PersonCollectionRelation
        attrs = {'class': 'table table-sortable'}


