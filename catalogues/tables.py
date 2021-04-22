import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from django.utils.html import format_html
from .models import *

from collections import defaultdict

from catalogues.models import PersonCatalogueRelation
from persons.models import Country
from mediate.columns import ActionColumn


# Catalogue table
class CatalogueTable(tables.Table):
    uuid = ActionColumn('catalogue_detail', 'change_catalogue', 'delete_catalogue', orderable=False)
    types = tables.Column(empty_values=(), verbose_name="Type(s)")
    owner = tables.Column(empty_values=(), orderable=False)
    number_of_lots = tables.Column(empty_values=(), orderable=False)
    number_of_items = tables.Column(empty_values=(), orderable=False)
    related_places = tables.Column(empty_values=(), verbose_name="Related places", orderable=False)
    countries = tables.Column(empty_values=(), verbose_name="Publication countries", orderable=False)

    class Meta:
        model = Catalogue
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
        return format_html('<a href="{}">{}</a>'.format(reverse_lazy('catalogue_detail', args=[record.pk]),
                                                        value[:50] + "..." if len(value) > 50 else value))

    def render_types(self, record):
        return format_html(
            ", ".join(
                [
                    '<a href="{}">{}</a>'.format(
                        reverse_lazy('change_cataloguecataloguetyperelation', args=[relation.pk]),
                        relation.type
                    )
                    for relation in record.cataloguecataloguetyperelation_set.all()
                ]
            )
        )

    def render_owner(self, record):
        owners = Person.objects.filter(personcataloguerelation__role__name__iexact="owner",
                                       personcataloguerelation__catalogue=record)
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
        relations = CataloguePlaceRelation.objects.filter(catalogue=record).prefetch_related('type')
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
        countries = Country.objects.filter(place__related_catalogues__catalogue=record).distinct()
        return format_html(", ".join(
            [
                '<a href="{}">{}</a>'.format(reverse_lazy('country_detail', args=[country.pk]), country)
                for country in countries
            ]
        ))



# CatalogueHeldBy table
class CatalogueHeldByTable(tables.Table):
    uuid = ActionColumn('catalogueheldby_detail', 'change_catalogueheldby', 'delete_catalogueheldby', orderable=False)

    class Meta:
        model = CatalogueHeldBy
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'library',
            'catalogue',
            'uuid'
        ]


# CatalogueType table
class CatalogueTypeTable(tables.Table):
    uuid = ActionColumn('cataloguetype_detail', 'change_cataloguetype', 'delete_cataloguetype', orderable=False)

    class Meta:
        model = CatalogueType
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'uuid'
        ]


# CatalogueCatalogueTypeRelation table
class CatalogueCatalogueTypeRelationTable(tables.Table):
    uuid = ActionColumn('cataloguecataloguetyperelation_detail', 'change_cataloguecataloguetyperelation',
                        'delete_cataloguecataloguetyperelation', orderable=False)

    class Meta:
        model = CatalogueCatalogueTypeRelation
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'catalogue',
            'type',
            'uuid'
        ]


# Collection table
class CollectionTable(tables.Table):
    uuid = ActionColumn('collection_detail', 'change_collection', 'delete_collection', orderable=False)

    class Meta:
        model = Collection
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'dataset',
            'uuid'
        ]


# CollectionYear table
class CollectionYearTable(tables.Table):
    uuid = ActionColumn('collectionyear_detail', 'change_collectionyear', 'delete_collectionyear', orderable=False)

    class Meta:
        model = CollectionYear
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'collection',
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
    catalogue = tables.RelatedLinkColumn()
    category = tables.RelatedLinkColumn()

    class Meta:
        model = Lot
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'catalogue',
            'category',
            'number_in_catalogue',
            'page_in_catalogue',
            'lot_as_listed_in_catalogue',
            'sales_price',
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
            'role',
            'uuid'
        ]


# PersonCatalogueRelationRole table
class PersonCatalogueRelationRoleTable(tables.Table):
    uuid = ActionColumn('personcataloguerelationrole_detail', 'change_personcataloguerelationrole',
                        'delete_personcataloguerelationrole', orderable=False)

    class Meta:
        model = PersonCatalogueRelationRole
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
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
            'uuid'
        ]


# CataloguePlaceRelation table
class CataloguePlaceRelationTable(tables.Table):
    uuid = ActionColumn('catalogueplacerelation_detail', 'change_catalogueplacerelation',
                        'delete_catalogueplacerelation', orderable=False)

    class Meta:
        model = CataloguePlaceRelation
        attr = {'class': 'table table-sortable'}
        sequence = [
            'catalogue',
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
            'catalogue',
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


# CataloguePlaceRelationType table
class CataloguePlaceRelationTypeTable(tables.Table):
    uuid = ActionColumn('catalogueplacerelationtype_detail', 'change_catalogueplacerelationtype', 'delete_catalogueplacerelationtype', orderable=False)

    class Meta:
        model = CataloguePlaceRelationType
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'uuid'
        ]
