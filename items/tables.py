import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from .models import *




# BookFormat table
class BookFormatTable(tables.Table):
    edit = tables.LinkColumn('bookformat_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = BookFormat
        attrs = {'class': 'table table-sortable'}


# Item table
class ItemTable(tables.Table):
    edit = tables.LinkColumn('item_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Item
        attrs = {'class': 'table table-sortable'}


# ItemAuthor table
class ItemAuthorTable(tables.Table):
    edit = tables.LinkColumn('itemauthor_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = ItemAuthor
        attrs = {'class': 'table table-sortable'}


# ItemBookFormatRelation table
class ItemBookFormatRelationTable(tables.Table):
    edit = tables.LinkColumn('itembookformatrelation_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = ItemBookFormatRelation
        attrs = {'class': 'table table-sortable'}


# ItemItemTypeRelation table
class ItemItemTypeRelationTable(tables.Table):
    edit = tables.LinkColumn('itemitemtyperelation_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = ItemItemTypeRelation
        attrs = {'class': 'table table-sortable'}


# ItemLanguageRelation table
class ItemLanguageRelationTable(tables.Table):
    edit = tables.LinkColumn('itemlanguagerelation_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = ItemLanguageRelation
        attrs = {'class': 'table table-sortable'}


# ItemMaterialDetailsRelation table
class ItemMaterialDetailsRelationTable(tables.Table):
    edit = tables.LinkColumn('itemmaterialdetailsrelation_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = ItemMaterialDetailsRelation
        attrs = {'class': 'table table-sortable'}


# ItemType table
class ItemTypeTable(tables.Table):
    edit = tables.LinkColumn('itemtype_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = ItemType
        attrs = {'class': 'table table-sortable'}


# ItemWorkRelation table
class ItemWorkRelationTable(tables.Table):
    edit = tables.LinkColumn('itemworkrelation_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = ItemWorkRelation
        attrs = {'class': 'table table-sortable'}


# Language table
class LanguageTable(tables.Table):
    view = tables.LinkColumn('language_detail', text='View', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Language
        attrs = {'class': 'table table-sortable'}


# MaterialDetails table
class MaterialDetailsTable(tables.Table):
    edit = tables.LinkColumn('materialdetails_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = MaterialDetails
        attrs = {'class': 'table table-sortable'}


# PersonItemRelation table
class PersonItemRelationTable(tables.Table):
    edit = tables.LinkColumn('personitemrelation_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = PersonItemRelation
        attrs = {'class': 'table table-sortable'}


# PersonItemRelationRole table
class PersonItemRelationRoleTable(tables.Table):
    edit = tables.LinkColumn('personitemrelationrole_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = PersonItemRelationRole
        attrs = {'class': 'table table-sortable'}


# Publication table
class PublicationTable(tables.Table):
    edit = tables.LinkColumn('publication_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Publication
        attrs = {'class': 'table table-sortable'}


# Publisher table
class PublisherTable(tables.Table):
    edit = tables.LinkColumn('publisher_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Publisher
        attrs = {'class': 'table table-sortable'}


# Subject table
class SubjectTable(tables.Table):
    edit = tables.LinkColumn('subject_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Subject
        attrs = {'class': 'table table-sortable'}


# Work table
class WorkTable(tables.Table):
    edit = tables.LinkColumn('work_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Work
        attrs = {'class': 'table table-sortable'}


# WorkAuthor table
class WorkAuthorTable(tables.Table):
    edit = tables.LinkColumn('workauthor_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = WorkAuthor
        attrs = {'class': 'table table-sortable'}


# WorkSubject table
class WorkSubjectTable(tables.Table):
    edit = tables.LinkColumn('worksubject_edit', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = WorkSubject
        attrs = {'class': 'table table-sortable'}


