import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from .models import *

from mediate.columns import ActionColumn


# BookFormat table
class BookFormatTable(tables.Table):
    uuid = ActionColumn('bookformat_detail', 'change_bookformat', 'delete_bookformat', orderable=False)

    class Meta:
        model = BookFormat
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'uuid'
        ]


# Item table
class ItemTable(tables.Table):
    uuid = ActionColumn('item_detail', 'change_item', 'delete_item', orderable=False)
    checkbox = tables.CheckBoxColumn(empty_values=(), orderable=False,
                                     attrs={'th__input': {'id': 'checkbox_column', 'title': 'Select/deselect all'}})
    people = tables.Column(empty_values=())
    works = tables.Column(empty_values=(), verbose_name=_("Works"))
    lot = tables.RelatedLinkColumn(order_by='lot__lot_as_listed_in_catalogue')
    sales_price = tables.Column(empty_values=(), order_by='lot__sales_price')
    catalogue = tables.Column(empty_values=())
    collection = tables.RelatedLinkColumn()
    number_of_volumes = tables.Column(verbose_name=_('Number of volumes'))
    material_details = tables.Column(empty_values=())
    manifestation = tables.LinkColumn()
    manage_works = tables.LinkColumn('add_workstoitem',
        text=format_html('<span class="glyphicon glyphicon-list" data-toggle="tooltip" data-original-title="Manage works"></span>'),
        args=[A('pk')], orderable=False, empty_values=())
    manage_persons = tables.LinkColumn('add_personstoitem',
         text=format_html('<span class="glyphicon glyphicon-list" data-toggle="tooltip" data-original-title="Manage people"></span>'),
         args=[A('pk')], orderable=False, empty_values=())

    class Meta:
        model = Item
        attrs = {'class': 'table table-sortable'}
        fields = [
            'short_title',
            'people',
            'works',
            'lot',
            'index_in_lot',
            'sales_price',
            'catalogue',
            'collection',
            'number_of_volumes',
            'book_format',
            'material_details',
            'manifestation',
            'uuid',
            'manage_works',
            'manage_persons',
            'checkbox',
        ]

    def render_checkbox(self, record):
        return format_html(
            '<input id="{}" class="checkbox" type="checkbox" name="checkbox"/>'.format(record.uuid)
        )

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

    def render_material_details(self, record):
        return ", ".join(MaterialDetails.objects.filter(items__item=record).values_list('description', flat=True))


# ItemAuthor table
class ItemAuthorTable(tables.Table):
    uuid = ActionColumn('itemauthor_detail', 'change_itemauthor', 'delete_itemauthor', orderable=False)

    class Meta:
        model = ItemAuthor
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'item',
            'author',
            'uuid'
        ]


# ItemItemTypeRelation table
class ItemItemTypeRelationTable(tables.Table):
    uuid = ActionColumn('itemitemtyperelation_detail', 'change_itemitemtyperelation', 'delete_itemitemtyperelation',
                        orderable=False)

    class Meta:
        model = ItemItemTypeRelation
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'item',
            'type',
            'uuid'
        ]


# ItemLanguageRelation table
class ItemLanguageRelationTable(tables.Table):
    uuid = ActionColumn('itemlanguagerelation_detail', 'change_itemlanguagerelation', 'delete_itemlanguagerelation',
                        orderable=False)

    class Meta:
        model = ItemLanguageRelation
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'item',
            'language',
            'uuid'
        ]


# ItemMaterialDetailsRelation table
class ItemMaterialDetailsRelationTable(tables.Table):
    uuid = ActionColumn('itemmaterialdetailsrelation_detail', 'change_itemmaterialdetailsrelation',
                        'delete_itemmaterialdetailsrelation', orderable=False)

    class Meta:
        model = ItemMaterialDetailsRelation
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'item',
            'material_details',
            'uuid'
        ]


# ItemType table
class ItemTypeTable(tables.Table):
    uuid = ActionColumn('itemtype_detail', 'change_itemtype', 'delete_itemtype', orderable=False)

    class Meta:
        model = ItemType
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'uuid'
        ]


# ItemWorkRelation table
class ItemWorkRelationTable(tables.Table):
    uuid = ActionColumn('itemworkrelation_detail', 'change_itemworkrelation', 'delete_itemworkrelation',
                        orderable=False)

    class Meta:
        model = ItemWorkRelation
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'item',
            'work',
            'uuid'
        ]


# Language table
class LanguageTable(tables.Table):
    uuid = ActionColumn('language_detail', 'change_language', 'delete_language',
                        orderable=False)

    class Meta:
        model = Language
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'language_code_2char',
            'language_code_3char',
            'description',
            'uuid'
        ]


# MaterialDetails table
class MaterialDetailsTable(tables.Table):
    uuid = ActionColumn('materialdetails_detail', 'change_materialdetails', 'delete_materialdetails',
                        orderable=False)

    class Meta:
        model = MaterialDetails
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'description',
            'uuid'
        ]


# PersonItemRelation table
class PersonItemRelationTable(tables.Table):
    uuid = ActionColumn('personitemrelation_detail', 'change_personitemrelation',
                        'delete_personitemrelation', orderable=False)

    class Meta:
        model = PersonItemRelation
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'person',
            'item',
            'role'
        ]


# PersonItemRelationRole table
class PersonItemRelationRoleTable(tables.Table):
    uuid = ActionColumn('personitemrelationrole_detail', 'change_personitemrelationrole',
                        'delete_personitemrelationrole', orderable=False)

    class Meta:
        model = PersonItemRelationRole
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'uuid'
        ]


# Manifestation table
class ManifestationTable(tables.Table):
    uuid = ActionColumn('manifestation_detail', 'change_manifestation', 'delete_manifestation', orderable=False)
    items = tables.Column(empty_values=(), verbose_name=_("Items"))
    place = tables.RelatedLinkColumn()
    url = tables.Column(linkify=lambda record: record.url)
    publisher = tables.Column(verbose_name=_("Publisher"), empty_values=())

    class Meta:
        model = Manifestation
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'items',
            'year',
            'year_tag',
            'terminus_post_quem',
            'place',
            'url',
            'publisher',
            'uuid'
        ]

    def render_items(self, record):
        items = Item.objects.filter(manifestation=record).distinct()
        return format_html(
            ", ".join(
                ['<a href="{}">{}</a>'.format(item.get_absolute_url(), item) for item in items]
            )
        )

    def render_publisher(self, record):
        publishers = Person.objects.filter(publisher__manifestation=record).distinct()
        return format_html(
            ", ".join(
                ['<a href="{}">{}</a>'.format(publisher.get_absolute_url(), publisher) for publisher in publishers]
            )
        )


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
    uuid = ActionColumn('subject_detail', 'change_subject', 'delete_subject', orderable=False)

    class Meta:
        model = Subject
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'uuid'
        ]


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
    uuid = ActionColumn('workauthor_detail', 'change_workauthor', 'delete_workauthor', orderable=False)

    class Meta:
        model = WorkAuthor
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'work',
            'author',
            'uuid'
        ]


# WorkSubject table
class WorkSubjectTable(tables.Table):
    uuid = ActionColumn('worksubject_detail', 'change_worksubject', 'delete_worksubject', orderable=False)

    class Meta:
        model = WorkSubject
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'work',
            'subject',
            'uuid'
        ]


