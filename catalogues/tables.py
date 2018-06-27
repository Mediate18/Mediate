import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from .models import *

from mediate.columns import ActionColumn

# Catalogue table
class CatalogueTable(tables.Table):
    uuid = ActionColumn('catalogue_detail', 'change_catalogue', 'delete_catalogue', orderable=False)
    transcription = tables.RelatedLinkColumn()
    collection = tables.RelatedLinkColumn()
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
            'type',
            'year_of_publication',
            'terminus_post_quem',
            'notes',
            'bibliography',
            'collection',
            'number_of_lots',
            'number_of_items'
        ]

    def render_full_title(self, value):
        return (value[:50] + "...") if len(value) > 50 else value

    def render_preface_and_paratexts(self, value):
        return (value[:50] + "...") if len(value) > 50 else value

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
    edit = tables.LinkColumn('change_collection', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Collection
        attrs = {'class': 'table table-sortable'}


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

    class Meta:
        model = Lot
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'catalogue',
            'bookseller_category_books',
            'bookseller_category_non_books',
            'number_in_catalogue',
            'item_as_listed_in_catalogue',
            'uuid'
        ]


# PersonCatalogueRelation table
class PersonCatalogueRelationTable(tables.Table):
    edit = tables.LinkColumn('change_personcataloguerelation', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = PersonCatalogueRelation
        attrs = {'class': 'table table-sortable'}


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


