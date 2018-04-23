import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from .models import *


# Catalogue table
class CatalogueTable(tables.Table):
    edit = tables.LinkColumn('catalogue_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Catalogue
        attrs = {'class': 'table table-sortable'}


# CatalogueHeldBy table
class CatalogueHeldByTable(tables.Table):
    edit = tables.LinkColumn('catalogueheldby_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = CatalogueHeldBy
        attrs = {'class': 'table table-sortable'}


# CatalogueType table
class CatalogueTypeTable(tables.Table):
    edit = tables.LinkColumn('cataloguetype_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = CatalogueType
        attrs = {'class': 'table table-sortable'}


# Collection table
class CollectionTable(tables.Table):
    edit = tables.LinkColumn('collection_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Collection
        attrs = {'class': 'table table-sortable'}


# CollectionYear table
class CollectionYearTable(tables.Table):
    edit = tables.LinkColumn('collectionyear_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = CollectionYear
        attrs = {'class': 'table table-sortable'}


# Library table
class LibraryTable(tables.Table):
    edit = tables.LinkColumn('library_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Library
        attrs = {'class': 'table table-sortable'}


# Lot table
class LotTable(tables.Table):
    edit = tables.LinkColumn('lot_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Lot
        attrs = {'class': 'table table-sortable'}


# PersonCatalogueRelation table
class PersonCatalogueRelationTable(tables.Table):
    edit = tables.LinkColumn('personcataloguerelation_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = PersonCatalogueRelation
        attrs = {'class': 'table table-sortable'}


# PersonCatalogueRelationRole table
class PersonCatalogueRelationRoleTable(tables.Table):
    edit = tables.LinkColumn('personcataloguerelationrole_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = PersonCatalogueRelationRole
        attrs = {'class': 'table table-sortable'}


# PersonCollectionRelation table
class PersonCollectionRelationTable(tables.Table):
    edit = tables.LinkColumn('personcollectionrelation_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = PersonCollectionRelation
        attrs = {'class': 'table table-sortable'}


