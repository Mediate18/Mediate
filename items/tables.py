import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from django.utils.html import format_html
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from .models import *


class ActionColumn(tables.Column):
    def __init__(self, url_name_view, url_name_change, url_name_delete, **kwargs):
        super().__init__(ActionColumn, **kwargs)
        self.url_name_view = url_name_view
        self.url_name_change = url_name_change
        self.url_name_delete = url_name_delete

    def render(self, value):
        html = format_html(
            """
            <div class="text-nowrap">
                <a href="{}">
                    <span class="glyphicon glyphicon-eye-open" data-toggle="tooltip" data-original-title="{}"></span>
                </a>
                <a href="{}">
                    <span class="glyphicon glyphicon-pencil" data-toggle="tooltip" data-original-title="{}"></span>
                    </a>
                <a class="delete-entry" href="" data-toggle="modal" data-target="#deleteModal" modal_url="{}">
                    <span class="glyphicon glyphicon-remove" data-toggle="tooltip" data-original-title="{}"></span>
                </a>
            </div>
            """.format(
                reverse_lazy(self.url_name_view, kwargs={'pk': value}),
                _('View'),
                reverse_lazy(self.url_name_change, kwargs={'pk': value}),
                _('Change'),
                reverse_lazy(self.url_name_delete, kwargs={'pk': value}),
                _('Delete'),
            )
        )
        return html


# BookFormat table
class BookFormatTable(tables.Table):
    edit = tables.LinkColumn('change_bookformat', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = BookFormat
        attrs = {'class': 'table table-sortable'}


# Item table
class ItemTable(tables.Table):
    uuid = ActionColumn('item_detail', 'change_item', 'delete_item', orderable=False)
    lot = tables.Column(order_by='lot__item_as_listed_in_catalogue')
    number_of_volumes = tables.Column(verbose_name=_('Number of volumes'))
    manage_works = tables.LinkColumn('add_workstoitem',
        text=format_html('<span class="glyphicon glyphicon-list" data-toggle="tooltip" data-original-title="Manage works"></span>'),
        args=[A('pk')], orderable=False, empty_values=())

    class Meta:
        model = Item
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'short_title',
            'lot',
            'collection',
            'number_of_volumes',
            'uuid',
            'manage_works'
        ]


# ItemAuthor table
class ItemAuthorTable(tables.Table):
    edit = tables.LinkColumn('change_itemauthor', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = ItemAuthor
        attrs = {'class': 'table table-sortable'}


# ItemBookFormatRelation table
class ItemBookFormatRelationTable(tables.Table):
    edit = tables.LinkColumn('change_itembookformatrelation', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = ItemBookFormatRelation
        attrs = {'class': 'table table-sortable'}


# ItemItemTypeRelation table
class ItemItemTypeRelationTable(tables.Table):
    edit = tables.LinkColumn('change_itemitemtyperelation', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = ItemItemTypeRelation
        attrs = {'class': 'table table-sortable'}


# ItemLanguageRelation table
class ItemLanguageRelationTable(tables.Table):
    edit = tables.LinkColumn('change_itemlanguagerelation', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = ItemLanguageRelation
        attrs = {'class': 'table table-sortable'}


# ItemMaterialDetailsRelation table
class ItemMaterialDetailsRelationTable(tables.Table):
    edit = tables.LinkColumn('change_itemmaterialdetailsrelation', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = ItemMaterialDetailsRelation
        attrs = {'class': 'table table-sortable'}


# ItemType table
class ItemTypeTable(tables.Table):
    edit = tables.LinkColumn('change_itemtype', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = ItemType
        attrs = {'class': 'table table-sortable'}


# ItemWorkRelation table
class ItemWorkRelationTable(tables.Table):
    edit = tables.LinkColumn('change_itemworkrelation', text='Edit', args=[A('pk')],
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
    edit = tables.LinkColumn('change_materialdetails', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = MaterialDetails
        attrs = {'class': 'table table-sortable'}


# PersonItemRelation table
class PersonItemRelationTable(tables.Table):
    edit = tables.LinkColumn('change_personitemrelation', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = PersonItemRelation
        attrs = {'class': 'table table-sortable'}


# PersonItemRelationRole table
class PersonItemRelationRoleTable(tables.Table):
    edit = tables.LinkColumn('change_personitemrelationrole', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = PersonItemRelationRole
        attrs = {'class': 'table table-sortable'}


# Publication table
class PublicationTable(tables.Table):
    edit = tables.LinkColumn('change_publication', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Publication
        attrs = {'class': 'table table-sortable'}


# Publisher table
class PublisherTable(tables.Table):
    edit = tables.LinkColumn('change_publisher', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Publisher
        attrs = {'class': 'table table-sortable'}


# Subject table
class SubjectTable(tables.Table):
    edit = tables.LinkColumn('change_subject', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Subject
        attrs = {'class': 'table table-sortable'}


# Work table
class WorkTable(tables.Table):
    edit = tables.LinkColumn('change_work', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Work
        attrs = {'class': 'table table-sortable'}


# WorkAuthor table
class WorkAuthorTable(tables.Table):
    edit = tables.LinkColumn('change_workauthor', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = WorkAuthor
        attrs = {'class': 'table table-sortable'}


# WorkSubject table
class WorkSubjectTable(tables.Table):
    edit = tables.LinkColumn('change_worksubject', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = WorkSubject
        attrs = {'class': 'table table-sortable'}


