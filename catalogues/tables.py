import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from django.utils.html import format_html
from .models import *
from django.conf import settings

from collections import defaultdict


from catalogues.models import PersonCollectionRelation
from items.models import Item
from persons.models import Country
from mediate.columns import ActionColumn, render_action_column


# Collection table
class CollectionTable(tables.Table):
    uuid = tables.Column(empty_values=(), verbose_name="", orderable=False)#ActionColumn('collection_detail', 'change_collection', 'delete_collection', orderable=False)
    full_title = tables.Column(empty_values=(), verbose_name="Catalogue full title(s)")
    types = tables.Column(empty_values=(), verbose_name="Catalogue type(s)")
    year_of_publication = tables.Column(empty_values=(), verbose_name="Year(s) of publication")
    owner = tables.Column(empty_values=(), orderable=False)
    number_of_lots = tables.Column(empty_values=(), orderable=False)
    number_of_items = tables.Column(empty_values=(), orderable=False)
    percentage_non_books = tables.Column(empty_values=(), orderable=False)
    related_places = tables.Column(empty_values=(), verbose_name="Related places", orderable=False)
    countries = tables.Column(empty_values=(), verbose_name="Publication countries", orderable=False)

    class Meta:
        model = Collection
        attrs = {'class': 'table table-sortable'}
        fields = [
            'short_title',
            'full_title',
            'types',
            'year_of_publication',
            'owner',
            'number_of_lots',
            'number_of_items',
            'percentage_non_books',
            'related_places',
            'countries'
        ]

    def render_uuid(self, record, value):
        change_dataset_perm = self.request.user.has_perm('catalogues.change_dataset', record.catalogue.first().dataset)

        url_name_change = 'change_collection' if change_dataset_perm else None
        url_name_delete = 'delete_collection' if change_dataset_perm else None

        return render_action_column(value, 'collection_detail', url_name_change, url_name_delete)

    def render_full_title(self, record, value):
        return format_html('<a href="{}">{}</a>'.format(reverse_lazy('collection_detail', args=[record.pk]),
                                                        value[:50] + "..." if len(value) > 50 else value))

    def render_types(self, record):
        return format_html(
            ", ".join(
                [
                    '<a href="{}">{}</a>'.format(
                        reverse_lazy('change_collectioncollectiontyperelation', args=[relation.pk]),
                        relation.type
                    )
                    for relation in record.collectioncollectiontyperelation_set.all()
                ]
            )
        )

    def render_year_of_publication(self, record):
        if not record.year_of_publication_end:
            return record.year_of_publication

        else:
            return f"{record.year_of_publication} - {record.year_of_publication_end}"

    def render_owner(self, record):
        owners = Person.objects.filter(personcollectionrelation__role__name__iexact="owner",
                                       personcollectionrelation__collection=record)
        return format_html(", ".join(
            [
                '<a href="{}">{}</a>'.format(reverse_lazy('change_person', args=[owner.pk]), owner)
                for owner in owners
            ]
        ))

    def render_number_of_lots(self, record):
        return record.lot_set.count()

    def render_number_of_items(self, record):
        item_count = record.item_count()

        if not record.has_uncountable_book_items():
            return item_count

        return format_html(
            '{}+ <span class="glyphicon glyphicon-info-sign" title="{}"></span>'.format(
                item_count,
                settings.UNCOUNTABLE_BOOK_ITEMS_MESSAGE
            )
        )

    def render_percentage_non_books(self, record):
        item_count = record.item_count()
        percentage = 0.00 if not item_count else \
            round(100 * Item.objects.filter(lot__collection=record, non_book=True).count() / record.item_count(), 2)
        return "{}%".format(percentage)

    def render_related_places(self, record):
        relations = CollectionPlaceRelation.objects.filter(collection=record).prefetch_related('type')
        type_dict = defaultdict(list)
        for relation in relations:
            type_dict[relation.type.name].append(relation.place)

        return format_html("<br/>".join([
            type.capitalize() + ": " + ", ".join([
                    '<a href="{}">{}</a>'.format(reverse_lazy('place_detail', args=[place.pk]), place)
                    for place in places
                ]) for type, places in type_dict.items()
            ]))

    def render_countries(self, record):
        countries = Country.objects.filter(place__related_collections__collection=record).distinct()
        return format_html(", ".join(
            [
                '<a href="{}">{}</a>'.format(reverse_lazy('country_detail', args=[country.pk]), country)
                for country in countries
            ]
        ))



# CollectionHeldBy table
class CollectionHeldByTable(tables.Table):
    uuid = ActionColumn('collectionheldby_detail', 'change_collectionheldby', 'delete_collectionheldby', orderable=False)

    class Meta:
        model = CollectionHeldBy
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'library',
            'collection',
            'uuid'
        ]


# CollectionType table
class CollectionTypeTable(tables.Table):
    uuid = ActionColumn('collectiontype_detail', 'change_collectiontype', 'delete_collectiontype', orderable=False)

    class Meta:
        model = CollectionType
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'uuid'
        ]


# CollectionCollectionTypeRelation table
class CollectionCollectionTypeRelationTable(tables.Table):
    uuid = ActionColumn('collectioncollectiontyperelation_detail', 'change_collectioncollectiontyperelation',
                        'delete_collectioncollectiontyperelation', orderable=False)

    class Meta:
        model = CollectionCollectionTypeRelation
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'collection',
            'type',
            'uuid'
        ]


# Catalogue table
class CatalogueTable(tables.Table):
    uuid = tables.Column(empty_values=(), verbose_name="", orderable=False)
    collections = tables.Column(empty_values=(), verbose_name="Collection(s)", orderable=False)
    lots = tables.Column(empty_values=(), verbose_name="Lots", orderable=False)
    items = tables.Column(empty_values=(), verbose_name="Items", orderable=False)

    class Meta:
        model = Catalogue
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'dataset',
            'collections',
            'shelf_mark',
            'lots',
            'items',
            'uuid'
        ]

    def render_uuid(self, record, value):
        change_dataset_perm = self.request.user.has_perm('catalogues.change_dataset',
                                                         record.dataset)

        url_name_change = 'change_catalogue' if change_dataset_perm else None
        url_name_delete = 'delete_catalogue' if change_dataset_perm else None

        return render_action_column(value, 'catalogue_detail', url_name_change, url_name_delete)

    def render_collections(self, record):
        return format_html(
            ", ".join([
                '<a href="{}">{}</a>'.format(
                    reverse_lazy('collection_detail', args=[collection.pk]),
                    collection
                )
                for collection in record.collection.all()
            ])
        )

    def render_items(self, record):
        item_count = record.item_count()

        return format_html(
            '<a href="{}?{}">'
            '<span class="glyphicon glyphicon-list" data-toggle="tooltip" '
            'data-original-title="List the items of {}"></span>'
            '</a>'
            ' {}'.format(
                reverse_lazy('items'),
                "&".join(["collection="+str(uuid) for uuid in record.collection.values_list("uuid", flat=True)]),
                record,
                item_count  
            )
        )

    def render_lots(self, record):
        lot_count = Lot.objects.filter(collection__catalogue=record).count()

        return format_html(
            '<a href="{}?{}">'
            '<span class="glyphicon glyphicon-list" data-toggle="tooltip" '
            'data-original-title="List the lots of {}"></span>'
            '</a>'
            ' {}'.format(
                reverse_lazy('lots'),
                "&".join(["collection="+str(uuid) for uuid in record.collection.values_list("uuid", flat=True)]),
                record,
                lot_count  
            )
        )


# CatalogueYear table
class CatalogueYearTable(tables.Table):
    uuid = ActionColumn('catalogueyear_detail', 'change_catalogueyear', 'delete_catalogueyear', orderable=False)

    class Meta:
        model = CatalogueYear
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'catalogue',
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
    collection = tables.RelatedLinkColumn()
    category = tables.RelatedLinkColumn()

    class Meta:
        model = Lot
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'collection',
            'category',
            'number_in_collection',
            'page_in_collection',
            'lot_as_listed_in_collection',
            'sales_price',
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
            'role',
            'uuid'
        ]


# PersonCollectionRelationRole table
class PersonCollectionRelationRoleTable(tables.Table):
    uuid = ActionColumn('personcollectionrelationrole_detail', 'change_personcollectionrelationrole',
                        'delete_personcollectionrelationrole', orderable=False)

    class Meta:
        model = PersonCollectionRelationRole
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
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
            'uuid'
        ]


# CollectionPlaceRelation table
class CollectionPlaceRelationTable(tables.Table):
    uuid = ActionColumn('collectionplacerelation_detail', 'change_collectionplacerelation',
                        'delete_collectionplacerelation', orderable=False)

    class Meta:
        model = CollectionPlaceRelation
        attr = {'class': 'table table-sortable'}
        sequence = [
            'collection',
            'place',
            'type',
            'uuid'
        ]

# Category table
class CategoryTable(tables.Table):
    uuid = ActionColumn('category_detail', 'change_category', 'delete_category', orderable=False)
    parent = tables.LinkColumn(verbose_name="Parent category")

    class Meta:
        model = Category
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'collection',
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


# CollectionPlaceRelationType table
class CollectionPlaceRelationTypeTable(tables.Table):
    uuid = ActionColumn('collectionplacerelationtype_detail', 'change_collectionplacerelationtype', 'delete_collectionplacerelationtype', orderable=False)

    class Meta:
        model = CollectionPlaceRelationType
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'uuid'
        ]
