from django.db.models import Count
import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
import itertools

from .models import *
from tagme.models import Tag

from mediate.columns import ActionColumn, render_action_column, AddInfoLinkMixin


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
class ItemTable(AddInfoLinkMixin, tables.Table):
    uuid = tables.Column(empty_values=(), verbose_name="", orderable=False)
    checkbox = tables.CheckBoxColumn(empty_values=(), orderable=False,
                                     attrs={'th__input': {'id': 'checkbox_column', 'title': 'Select/deselect all'}})
    people = tables.Column(empty_values=(), orderable=False)
    works = tables.Column(empty_values=(), verbose_name=_("Works"))
    lot = tables.Column(order_by='lot__lot_as_listed_in_collection', )
    collection = tables.Column(empty_values=(), order_by='lot__collection__short_title')
    number_of_volumes = tables.Column(empty_values=(), verbose_name=_('Number of volumes'))
    material_details = tables.Column(empty_values=(), orderable=False)
    edition = tables.Column(empty_values=(), orderable=False)
    manage_works = tables.LinkColumn('add_workstoitem',
        text=format_html('<span class="glyphicon glyphicon-list" data-toggle="tooltip" data-original-title="Manage works"></span>'),
        args=[A('pk')], orderable=False, empty_values=())
    manage_persons = tables.LinkColumn('add_personstoitem',
         text=format_html('<span class="glyphicon glyphicon-list" data-toggle="tooltip" data-original-title="Manage people"></span>'),
         args=[A('pk')], orderable=False, empty_values=())
    languages = tables.Column(empty_values=(), verbose_name=_("Languages"), orderable=False)
    parisian_category = tables.Column(empty_values=(), verbose_name=_("Parisian category"))
    item_type = tables.Column(empty_values=(), orderable=False)
    tags = tables.Column(empty_values=(), orderable=False)

    class Meta:
        model = Item
        attrs = {'class': 'table table-sortable'}
        fields = [
            'short_title',
            'people',
            'works',
            'lot',
            'index_in_lot',
            'collection',
            'number_of_volumes',
            'book_format',
            'material_details',
            'edition',
            'languages',
            'parisian_category',
            'item_type',
            'tags',
            'uncountable_book_items',
            'uuid',
            'manage_works',
            'manage_persons',
            'checkbox',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_info_link("parisian_category", 'parisiancategories')
        self.data.data = self.data.data.prefetch_related(
            'lot',
            'lot__collection',
            'lot__collection__catalogue__dataset',
            'personitemrelation_set__role',
            'book_format',
            'works',
            'works__work',
            'edition',
            'parisian_category',
            'tags',
        )

    def render_uuid(self, record, value):
        change_dataset_perm = self.request.user.has_perm('catalogues.change_dataset',
                                                         record.lot.collection.catalogue.first().dataset)

        url_name_change = 'change_item' if change_dataset_perm else None
        url_name_delete = 'delete_item' if change_dataset_perm else None

        return render_action_column(value, 'item_detail', url_name_change, url_name_delete)

    def render_lot(self, record):
        return format_html(
            '<div class="col-xs-11 expandable-cell collapsed-cell"><a href="{}">{}</a></div>'
            '<div class="col-xs-1">'
            '<span class="expand-cell glyphicon glyphicon-chevron-down" title="Expand"></span>'
            '<span class="collapse-cell glyphicon glyphicon-chevron-up" title="Collapse"></span>'
            '</div>',
            reverse_lazy('change_lot', args=[record.lot_id]), record.lot.lot_as_listed_in_collection
        )

    def render_checkbox(self, record):
        return format_html(
            '<input id="{}" class="checkbox" type="checkbox" name="checkbox"/>'.format(record.uuid)
        )

    def render_people(self, record):
        person_item_relations = record.personitemrelation_set.all() #
        relation_groups = []
        for role in set([relation.role for relation in person_item_relations]):
            role_relations = person_item_relations.filter(role=role)
            persons = []
            for relation in role_relations:
                person = relation.person
                name = person.short_name
                viaf = person.viaf_id
                person_entry = "<a href='{}'>{}</a>".format(reverse_lazy('person_detail', args=[person.pk]), name)
                if viaf:
                    person_entry += " (<a target='blank' href='{}'>VIAF</a>)".format(viaf)
                if relation.notes:
                    person_entry += ' <a href="{}"><span class="glyphicon glyphicon-comment" title="{}"></span></a>'\
                        .format(relation.get_absolute_url(), relation.notes)
                persons.append(person_entry)

            relation_groups.append(
                role.name.capitalize() + ": " + ", ".join(persons)
            )
        return format_html("<br/> ".join(relation_groups))

    def render_works(self, record):
        item_work_relations = record.works.all()
        work_entries = []
        for relation in item_work_relations:
            work = relation.work
            viaf = work.viaf_id
            work_entry = "<a href='{}'>{}</a>".format(reverse_lazy('change_work', args=[work.pk]), work.title)
            if viaf:
                work_entry += " (<a target='blank' href='{}'>VIAF</a>)".format(viaf)
            work_entries.append(work_entry)
        return format_html(" | ".join(work_entries))

    def render_collection(self, record):
        try:
            return format_html('<a href="{}">{}</a>'.format(
                reverse_lazy('collection_detail', args=[str(record.lot.collection_id)]),
                str(record.lot.collection))
            )
        except AttributeError:
            # Record has not lot or lot has no collection
            return ''

    def render_number_of_volumes(self, record):
        return record.number_of_volumes or format_html("&mdash;")

    def render_material_details(self, record):
        return ", ".join(MaterialDetails.objects.filter(items__item=record).values_list('description', flat=True))

    def render_edition(self, record):
        year = record.edition.get_year_range_str()
        year_str = year if year else ""
        publishers_str = ", ".join(
            Person.objects.filter(publisher__edition=record.edition_id).values_list('short_name', flat=True)
        )
        places_str = ", ".join(
            Place.objects.filter(publicationplace__edition=record.edition_id).values_list('name', flat=True)
        )
        return f'{places_str}{": " if places_str else ""}{publishers_str}{", " if publishers_str and year_str else ""}{year_str}'

    def render_languages(self, record):
        language_names = [format_html(language.name) for language in Language.objects.filter(items__item=record)]
        return format_html(
            '<div class="col-xs-11 expandable-cell collapsed-cell">{}</div>'
            '<div class="col-xs-1">'
            '<span class="expand-cell glyphicon glyphicon-chevron-down" title="Expand"></span>'
            '<span class="collapse-cell glyphicon glyphicon-chevron-up" title="Collapse"></span>'
            '</div>',
            mark_safe(", ".join(language_names))
        )

    def render_parisian_category(self, record):
        try:
            return record.parisian_category.name
        except:
            return ""

    def render_item_type(self, record):
        return ", ".join(ItemType.objects.filter(itemitemtyperelation__item=record).values_list('name', flat=True))

    def render_tags(self, record):
        return ", ".join([str(taggedentity.tag) for taggedentity in record.tags.all()])

    # All value_XX methods are for the table export
    def value_lot(self, record):
        return record.lot.lot_as_listed_in_collection

    def value_people(self, record):
        person_item_relations = PersonItemRelation.objects.filter(item=record)
        relation_groups = []
        for role in set([relation.role for relation in person_item_relations]):
            role_relations = person_item_relations.filter(role=role)
            persons = []
            for relation in role_relations:
                person = relation.person
                name = person.short_name
                person_entry = name
                persons.append(person_entry)

            relation_groups.append(
                role.name.capitalize() + ": " + ", ".join(persons)
            )
        return "\n".join(relation_groups)

    def value_works(self, record):
        item_work_relations = ItemWorkRelation.objects.filter(item=record)
        work_entries = []
        for relation in item_work_relations:
            work = relation.work
            work_entry = work.title
            work_entries.append(work_entry)
        return " | ".join(work_entries)

    def value_collection(self, record):
        return str(record.lot.collection) or ""

    def value_sales_price(self, record):
        return record.lot.sales_price or ""

    def value_number_of_volumes(self, record):
        return record.number_of_volumes or ""


# Item table
class TaggedItemTable(tables.Table):
    people = tables.Column(empty_values=())
    works = tables.Column(empty_values=(), verbose_name=_("Works"))
    lot = tables.Column(order_by='lot__lot_as_listed_in_collection', )
    sales_price = tables.Column(empty_values=(), order_by='lot__sales_price')
    collection = tables.Column(empty_values=(), order_by='lot__collection__short_title')
    number_of_volumes = tables.Column(empty_values=(), verbose_name=_('Number of volumes'))
    material_details = tables.Column(empty_values=())

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
            'collection',
            'catalogue',
            'number_of_volumes',
            'book_format',
            'material_details',
            'edition',
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
                person_entry = name
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

    def render_collection(self, record):
        return format_html(str(record.lot.collection))

    def render_sales_price(self, record):
        return record.lot.sales_price

    def render_number_of_volumes(self, record):
        return record.number_of_volumes or format_html("&mdash;")

    def render_material_details(self, record):
        return ", ".join(MaterialDetails.objects.filter(items__item=record).values_list('description', flat=True))

    # All value_XX methods are for the table export
    def value_lot(self, record):
        return record.lot.lot_as_listed_in_collection

    def value_people(self, record):
        person_item_relations = PersonItemRelation.objects.filter(item=record)
        relation_groups = []
        for role in set([relation.role for relation in person_item_relations]):
            role_relations = person_item_relations.filter(role=role)
            persons = []
            for relation in role_relations:
                person = relation.person
                name = person.short_name
                person_entry = name
                persons.append(person_entry)

            relation_groups.append(
                role.name.capitalize() + ": " + ", ".join(persons)
            )
        return "\n".join(relation_groups)

    def value_works(self, record):
        item_work_relations = ItemWorkRelation.objects.filter(item=record)
        work_entries = []
        for relation in item_work_relations:
            work = relation.work
            work_entry = work.title
            work_entries.append(work_entry)
        return " | ".join(work_entries)

    def value_collection(self, record):
        return str(record.lot.collection) or ""

    def value_sales_price(self, record):
        return record.lot.sales_price or ""

    def value_number_of_volumes(self, record):
        return record.number_of_volumes or ""


# Item Tag ranking table
class ItemTagRankingTable(tables.Table):
    row_index = tables.Column(empty_values=(), orderable=False, verbose_name="")
    item_count = tables.Column(empty_values=(), verbose_name=_("# items"))

    class Meta:
        model = Tag
        attrs = {'class': 'table table-sortable'}
        fields = [
            'row_index',
            'item_count',
            'name',
            'value',
        ]

    def render_row_index(self):
        self.row_index = getattr(self, 'row_index', itertools.count(self.page.start_index()))
        return next(self.row_index)


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
    row_index = tables.Column(empty_values=(), orderable=False, verbose_name="")
    item_count = tables.Column(empty_values=(), verbose_name=_("# items"))
    uuid = ActionColumn('language_detail', 'change_language', 'delete_language',
                        orderable=False)

    class Meta:
        model = Language
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'row_index',
            'item_count',
            'name',
            'language_code_2char',
            'language_code_3char',
            'description',
            'uuid'
        ]

    def render_row_index(self):
        self.row_index = getattr(self, 'row_index', itertools.count(self.page.start_index()))
        return next(self.row_index)

    def render_item_count(self, record):
        return format_html(
            '<a href="{}?language={}">{}</a>'.format(reverse_lazy('items'), record.uuid, record.item_count)
        )



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


# Edition table
class EditionTable(tables.Table):
    uuid = ActionColumn('edition_detail', 'change_edition', 'delete_edition', orderable=False)
    checkbox = tables.CheckBoxColumn(empty_values=(), orderable=False,
                                     attrs={'th__input': {'id': 'checkbox_column', 'title': 'Select/deselect all'}})
    items = tables.Column(empty_values=(), verbose_name=_("Items"))
    place = tables.RelatedLinkColumn()
    url = tables.Column(linkify=lambda record: record.url)
    publisher = tables.Column(verbose_name=_("Publisher"), empty_values=())
    year_of_publication = tables.Column(empty_values=(), verbose_name=_("Year of publication"))

    class Meta:
        model = Edition
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'items',
            'year_of_publication',
            'year_tag',
            'terminus_post_quem',
            'place',
            'url',
            'publisher',
            'uuid',
            'checkbox'
        ]
        exclude = ['year_start', 'year_end']

    def render_items(self, record):
        items = Item.objects.filter(edition=record).distinct()
        return format_html(
            ", ".join(
                ['<a href="{}">{}</a>'.format(item.get_absolute_url(), item) for item in items]
            )
        )

    def render_publisher(self, record):
        publishers = Person.objects.filter(publisher__edition=record).distinct()
        return format_html(
            ", ".join(
                ['<a href="{}">{}</a>'.format(publisher.get_absolute_url(), publisher) for publisher in publishers]
            )
        )

    def render_checkbox(self, record):
        return format_html(
            '<input id="{}" class="checkbox" type="checkbox" name="checkbox"/>'.format(record.uuid)
        )
    
    def render_year_of_publication(self, record):
        year_range_str = "{}".format(record.year_start) if record.year_start else "?"
        year_range_str += " - {}".format(record.year_end) if record.year_end else ""
        year_range_str = "—" if year_range_str == "?" else year_range_str
        return year_range_str


# EditionRanking table
class EditionRankingTable(EditionTable):
    row_index = tables.Column(empty_values=(), orderable=False, verbose_name="")
    item_count = tables.Column(empty_values=(), verbose_name=_("# items"))
    collection_count = tables.Column(empty_values=(), verbose_name=_("# collections"))

    class Meta:
        model = Edition
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'row_index',
            'item_count',
            'collection_count',
            'items',
            'year_of_publication',
            'year_tag',
            'terminus_post_quem',
            'place',
            'url',
            'publisher',
            'uuid',
            'checkbox'
        ]
        exclude = ['year_start', 'year_end']

    def render_row_index(self):
        self.row_index = getattr(self, 'row_index', itertools.count(self.page.start_index()))
        return next(self.row_index)


# Publisher table
class PublisherTable(tables.Table):
    uuid = ActionColumn('publisher_detail', 'change_publisher', 'delete_publisher', orderable=False)
    publisher = tables.RelatedLinkColumn()
    edition = tables.RelatedLinkColumn()

    class Meta:
        model = Publisher
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'publisher',
            'edition',
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
    uuid = tables.Column(empty_values=(), verbose_name="", orderable=False)
    parisian_category = tables.Column(empty_values=(), verbose_name=_("Parisian category"), orderable=False)
    checkbox = tables.CheckBoxColumn(empty_values=(), orderable=False,
                                     attrs={'th__input': {'id': 'checkbox_column', 'title': 'Select/deselect all'}})
    viaf_id = tables.Column(empty_values=())

    class Meta:
        model = Work
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'title',
            'viaf_id',
            'parisian_category',
            'uuid'
        ]

    def render_uuid(self, record, value):
        url_name_change = 'change_work' if self.request.user.has_perm('items.change_work') else None
        url_name_delete = 'delete_work' if self.request.user.has_perm('items.delete_work') else None

        return render_action_column(value, 'work_detail', url_name_change, url_name_delete)

    def render_parisian_category(self, record, value):
        parisian_categories = ParisianCategory.objects.filter(item__works__work=record)\
            .annotate(item_count=Count("item"))
        return format_html(
            " | ".join([
                f'<a href="{parisian_category.get_absolute_url()}">{parisian_category.name}</a> ({parisian_category.item_count} items)'
                for parisian_category in parisian_categories
            ])
        )

    def render_checkbox(self, record):
        return format_html(
            '<input id="{}" class="checkbox" type="checkbox" name="checkbox"/>'.format(record.uuid)
        )

    def render_viaf_id(self, value):
        if value:
            return format_html('<a target="blank" href="{}">{}</a>'.format(
                value, value
            ))
        else:
            return format_html('-')


# WorkRanking table
class WorkRankingTable(WorkTable):
    row_index = tables.Column(empty_values=(), orderable=False, verbose_name="")
    item_count = tables.Column(empty_values=(), verbose_name=_("# items"))
    collection_count = tables.Column(empty_values=(), verbose_name=_("# collections"),
                                    order_by=("collection_count", "item_count"))

    class Meta:
        model = Work
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'row_index',
            'item_count',
            'collection_count',
            'title',
            'viaf_id',
            'uuid'
        ]

    def render_row_index(self):
        self.row_index = getattr(self, 'row_index', itertools.count(self.page.start_index()))
        return next(self.row_index)


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


