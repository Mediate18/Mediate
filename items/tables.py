import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from django.utils.html import format_html
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from .models import *

from mediate.columns import ActionColumn


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
    people = tables.Column(empty_values=())
    lot = tables.RelatedLinkColumn(order_by='lot__item_as_listed_in_catalogue')
    catalogue = tables.Column(empty_values=())
    collection = tables.RelatedLinkColumn()
    number_of_volumes = tables.Column(verbose_name=_('Number of volumes'))
    manage_works = tables.LinkColumn('add_workstoitem',
        text=format_html('<span class="glyphicon glyphicon-list" data-toggle="tooltip" data-original-title="Manage works"></span>'),
        args=[A('pk')], orderable=False, empty_values=())

    class Meta:
        model = Item
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'short_title',
            'people',
            'lot',
            'catalogue',
            'collection',
            'number_of_volumes',
            'uuid',
            'manage_works'
        ]

    def render_people(self, record):
        relation_roles = PersonItemRelationRole.objects.filter(personitemrelation__item=record).distinct()
        relation_groups = []
        for role in relation_roles:
            person_item_relations = Person.objects.filter(personitemrelation__item=record, personitemrelation__role=role)
            relation_groups.append(
                role.name + ": " + ", ".join([person.short_name for person in person_item_relations])
            )
        return format_html("; ".join(relation_groups))

    def render_catalogue(self, record):
        return format_html('<a href="{}">{}</a>'.format(
            reverse_lazy('catalogue_detail', args=[str(record.lot.catalogue.uuid)]),
            str(record.lot.catalogue))
        )


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
    uuid = ActionColumn('work_detail', 'change_work', 'delete_work', orderable=False)
    viaf_id = tables.Column(empty_values=())

    class Meta:
        model = Work
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'title',
            'viaf_id',
            'uuid'
        ]

    def render_viaf_id(self, value):
        if value:
            return format_html('<a target="blank" href="{}">{}</a>'.format(
                value, value
            ))
        else:
            return format_html('-')


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


