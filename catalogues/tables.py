import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from django.utils.html import format_html
from .models import *

from collections import defaultdict

from catalogues.models import PersonCollectionRelation
from persons.models import Country
from mediate.columns import ActionColumn


# Collection table
class CollectionTable(tables.Table):
    uuid = ActionColumn('collection_detail', 'change_collection', 'delete_collection', orderable=False)
    types = tables.Column(empty_values=(), verbose_name="Type(s)")
    owner = tables.Column(empty_values=(), orderable=False)
    number_of_lots = tables.Column(empty_values=(), orderable=False)
    number_of_items = tables.Column(empty_values=(), orderable=False)
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
            'related_places',
            'countries'
        ]

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
        return record.item_count()

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


# Collection_TMP table
class Collection_TMPTable(tables.Table):
    uuid = ActionColumn('collection_tmp_detail', 'change_collection_tmp', 'delete_collection_tmp', orderable=False)

    class Meta:
        model = Collection_TMP
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'dataset',
            'uuid'
        ]


# Collection_TMPYear table
class Collection_TMPYearTable(tables.Table):
    uuid = ActionColumn('collection_tmpyear_detail', 'change_collection_tmpyear', 'delete_collection_tmpyear', orderable=False)

    class Meta:
        model = Collection_TMPYear
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'collection_tmp',
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


# PersonCollection_TMPRelation table
class PersonCollection_TMPRelationTable(tables.Table):
    uuid = ActionColumn('personcollection_tmprelation_detail', 'change_personcollection_tmprelation',
                        'delete_personcollection_tmprelation', orderable=False)

    class Meta:
        model = PersonCollection_TMPRelation
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'person',
            'collection_tmp',
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
