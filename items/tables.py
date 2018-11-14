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
    works = tables.Column(empty_values=(), verbose_name=_("Works"))
    lot = tables.RelatedLinkColumn(order_by='lot__lot_as_listed_in_catalogue')
    sales_price = tables.Column(empty_values=(), order_by='lot__sales_price')
    catalogue = tables.Column(empty_values=())
    collection = tables.RelatedLinkColumn()
    number_of_volumes = tables.Column(verbose_name=_('Number of volumes'))
    manage_works = tables.LinkColumn('add_workstoitem',
        text=format_html('<span class="glyphicon glyphicon-list" data-toggle="tooltip" data-original-title="Manage works"></span>'),
        args=[A('pk')], orderable=False, empty_values=())
    manage_persons = tables.LinkColumn('add_personstoitem',
         text=format_html('<span class="glyphicon glyphicon-list" data-toggle="tooltip" data-original-title="Manage people"></span>'),
         args=[A('pk')], orderable=False, empty_values=())

    class Meta:
        model = Item
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'short_title',
            'people',
            'works',
            'lot',
            'sales_price',
            'catalogue',
            'collection',
            'number_of_volumes',
            'book_format',
            'uuid',
            'manage_works',
            'manage_persons'
        ]

    def render_people(self, record):
        person_item_relations = PersonItemRelation.objects.filter(item=record)
        relation_groups = []
        for role in set([relation.role for relation in person_item_relations]):
            role_relations = person_item_relations.filter(role=role)
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

    def render_works(self, record):
        item_work_relations = ItemWorkRelation.objects.filter(item=record)
        work_entries = []
        for relation in item_work_relations:
            work = relation.work
            viaf = work.viaf_id
            work_entry = "<a href='{}'>{}</a>".format(reverse_lazy('change_work', args=[work.pk]), work.title)
            if viaf:
                work_entry += " (<a target='blank' href='{}'>VIAF</a>)".format(viaf)
            work_entries.append(work_entry)
        return format_html(" | ".join(work_entries))


    def render_catalogue(self, record):
        return format_html('<a href="{}">{}</a>'.format(
            reverse_lazy('catalogue_detail', args=[str(record.lot.catalogue.uuid)]),
            str(record.lot.catalogue))
        )

    def render_sales_price(self, record):
        return record.lot.sales_price


# ItemAuthor table
class ItemAuthorTable(tables.Table):
    edit = tables.LinkColumn('change_itemauthor', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = ItemAuthor
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


# Manifestation table
class ManifestationTable(tables.Table):
    uuid = ActionColumn('manifestation_detail', 'change_manifestation', 'delete_manifestation', orderable=False)
    item = tables.RelatedLinkColumn()
    place = tables.RelatedLinkColumn()
    url = tables.Column(linkify=lambda record: record.url)

    class Meta:
        model = Manifestation
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'item',
            'year',
            'year_tag',
            'terminus_post_quem',
            'place',
            'url'
        ]


# Publisher table
class PublisherTable(tables.Table):
    uuid = ActionColumn('publisher_detail', 'change_publisher', 'delete_publisher', orderable=False)
    publisher = tables.RelatedLinkColumn()
    manifestation = tables.RelatedLinkColumn()

    class Meta:
        model = Publisher
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'publisher',
            'manifestation',
        ]


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


