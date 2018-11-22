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
    types = tables.Column(empty_values=(), verbose_name="Type(s)")
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
            'types',
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

    def render_types(self, record):
        return format_html(
            ", ".join(
                [
                    '<a href="{}">{}</a>'.format(
                        reverse_lazy('change_cataloguecataloguetyperelation', args=[relation.pk]),
                        relation.type
                    )
                    for relation in record.cataloguecataloguetyperelation_set.all()
                ]
            )
        )

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
    uuid = ActionColumn('catalogueheldby_detail', 'change_catalogueheldby', 'delete_catalogueheldby', orderable=False)

    class Meta:
        model = CatalogueHeldBy
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'library',
            'catalogue',
            'uuid'
        ]


# CatalogueType table
class CatalogueTypeTable(tables.Table):
    uuid = ActionColumn('cataloguetype_detail', 'change_cataloguetype', 'delete_cataloguetype', orderable=False)

    class Meta:
        model = CatalogueType
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'uuid'
        ]


# CatalogueCatalogueTypeRelation table
class CatalogueCatalogueTypeRelationTable(tables.Table):
    uuid = ActionColumn('cataloguecataloguetyperelation_detail', 'change_cataloguecataloguetyperelation',
                        'delete_cataloguecataloguetyperelation', orderable=False)

    class Meta:
        model = CatalogueCatalogueTypeRelation
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'catalogue',
            'type',
            'uuid'
        ]


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
    uuid = ActionColumn('collectionyear_detail', 'change_collectionyear', 'delete_collectionyear', orderable=False)

    class Meta:
        model = CollectionYear
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'collection',
            'year',
            'uuid'
        ]


# Library table
class LibraryTable(tables.Table):
    uuid = ActionColumn('library_detail', 'change_library', 'delete_library', orderable=False)

    class Meta:
        model = Library
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'uuid'
        ]


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
    uuid = ActionColumn('personcataloguerelationrole_detail', 'change_personcataloguerelationrole',
                        'delete_personcataloguerelationrole', orderable=False)

    class Meta:
        model = PersonCatalogueRelationRole
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'uuid'
        ]


# PersonCollectionRelation table
class PersonCollectionRelationTable(tables.Table):
    uuid = ActionColumn('personcollectionrelation_detail', 'change_personcollectionrelation',
                        'delete_personcollectionrelation', orderable=False)

    class Meta:
        model = PersonCollectionRelation
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'person',
            'collection',
            'uuid'
        ]


# Category table
class CategoryTable(tables.Table):
    uuid = ActionColumn('category_detail', 'change_category', 'delete_category', orderable=False)

    class Meta:
        model = Category
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'catalogue',
            'parent',
            'bookseller_category',
            'parisian_category',
            'uuid'
        ]


# ParisianCategory table
class ParisianCategoryTable(tables.Table):
    uuid = ActionColumn('parisiancategory_detail', 'change_parisiancategory', 'delete_parisiancategory', orderable=False)

    class Meta:
        model = ParisianCategory
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'description',
            'uuid'
        ]
