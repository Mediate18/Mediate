import django_filters
from django.db.models import Count, Q
from django_select2.forms import Select2MultipleWidget, ModelSelect2MultipleWidget
from .models import *
from mediate.tools import filter_multiple_words
from persons.models import Profession, Religion, Place, Country
from tagme.models import Tag


# Collection filter
class CollectionFilter(django_filters.FilterSet):
    short_title = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    full_title = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    types = django_filters.ModelMultipleChoiceFilter(
        label='Types',
        queryset=CollectionType.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
        method='collection_types_filter'
    )
    year_of_publication = django_filters.RangeFilter(
        widget=django_filters.widgets.RangeWidget(),
        method='year_of_publication_filter'
    )
    terminus_post_quem = django_filters.BooleanFilter(widget=django_filters.widgets.BooleanWidget())
    number_of_items = django_filters.Filter(label='Number of items', method='number_of_items_filter',
                                            widget=django_filters.widgets.RangeWidget())
    number_of_lots = django_filters.Filter(label='Number of lots', method='number_of_lots_filter',
                                            widget=django_filters.widgets.RangeWidget())
    publisher = django_filters.ModelMultipleChoiceFilter(
        label="Publisher",
        queryset=Person.objects.filter(personcollectionrelation__role__name='publisher'),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
        field_name='personcollectionrelation__person',
        lookup_expr='in'
    )
    owner_gender = django_filters.MultipleChoiceFilter(
        label="Owner gender",
        choices=Person.SEX_CHOICES,
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        method='owner_gender_filter'
    )
    owner_profession = django_filters.ModelMultipleChoiceFilter(
        label="Owner profession",
        queryset=Profession.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        method='owner_profession_filter'
    )
    owner_religion = django_filters.ModelMultipleChoiceFilter(
        label="Owner religion",
        queryset=Religion.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        method='owner_religion_filter'
    )
    place = django_filters.ModelMultipleChoiceFilter(
        label="Place",
        queryset=Place.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        method='place_filter'
    )
    country = django_filters.ModelMultipleChoiceFilter(
        label="Country",
        queryset=Country.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        method='country_filter'
    )
    tag = django_filters.ModelMultipleChoiceFilter(
        label="Tag",
        queryset=Tag.objects.filter(Q(namespace='Catalogue') | Q(namespace='Collection')),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            queryset=Tag.objects.filter(Q(namespace='Catalogue') | Q(namespace='Collection')),
            search_fields=['name__icontains', 'value__icontains']
        ),
        method='tag_filter'
    )

    class Meta:
        model = Collection
        fields = [
            'short_title',
            'full_title',
            'types',
            'year_of_publication',
            'terminus_post_quem',
            'number_of_items',
            'number_of_lots'
        ]

    def multiple_words_filter(self, queryset, name, value):
        return filter_multiple_words(self.filters[name].lookup_expr, queryset, name, value)

    def collection_types_filter(self, queryset, name, value):
        if value:
            return queryset.filter(collectioncollectiontyperelation__type__in=value)
        else:
            return queryset

    def year_of_publication_filter(self, queryset, name, value):
        if not value:
            return queryset

        # The RangeWidget gives a slice, i.e. 'value' is a slice
        if not value.stop:
            return queryset.filter(
                (Q(year_of_publication__lte=value.start) & Q(year_of_publication_end__gte=value.start))
                | (Q(year_of_publication=value.start) & Q(year_of_publication_end__isnull=True))
            )

        start_in_range = (Q(year_of_publication__lte=value.start) & Q(year_of_publication_end__gte=value.start)) \
                         | (Q(year_of_publication=value.start) & Q(year_of_publication_end__isnull=True))
        end_in_range = (Q(year_of_publication__lte=value.stop) & Q(year_of_publication_end__gte=value.start)) \
                       | (Q(year_of_publication=value.start) & Q(year_of_publication_end__isnull=True))

        return queryset.filter(start_in_range | end_in_range)

    def number_of_items_filter(self, queryset, name, value):
        if any(value):
            queryset = queryset.annotate(num_items=Count('lot__item'))
            if value[0]:
                queryset = queryset.filter(num_items__gte=value[0])
            if value[1]:
                queryset = queryset.filter(num_items__lte=value[1])
        return queryset

    def number_of_lots_filter(self, queryset, name, value):
        if any(value):
            queryset = queryset.annotate(num_items=Count('lot'))
            if value[0]:
                queryset = queryset.filter(num_items__gte=value[0])
            if value[1]:
                queryset = queryset.filter(num_items__lte=value[1])
        return queryset

    def owner_gender_filter(self, queryset, name, value):
        if value:
            return queryset.filter(personcollectionrelation__role__name='owner',
                                   personcollectionrelation__person__sex__in=value)
        return queryset

    def owner_profession_filter(self, queryset, name, value):
        if value:
            return queryset.filter(personcollectionrelation__role__name='owner',
                                   personcollectionrelation__person__personprofession__profession__in=value)
        return queryset

    def owner_religion_filter(self, queryset, name, value):
        if value:
            return queryset.filter(personcollectionrelation__role__name='owner',
                                   personcollectionrelation__person__religiousaffiliation__religion__in=value)
        return queryset

    def place_filter(self, queryset, name, value):
        if value:
            return queryset.filter(related_places__place__in=value)
        return queryset

    def country_filter(self, queryset, name, value):
        if value:
            return queryset.filter(related_places__place__country__in=value)
        return queryset

    def tag_filter(self, queryset, name, value):
        if value:
            return queryset.filter(tags__tag__in=value)
        return queryset


# CollectionHeldBy filter
class CollectionHeldByFilter(django_filters.FilterSet):
    library = django_filters.ModelMultipleChoiceFilter(
        queryset=Library.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
    )
    collection = django_filters.ModelMultipleChoiceFilter(
        queryset=Collection.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
    )

    class Meta:
        model = CollectionHeldBy
        exclude = ['uuid']


# CollectionType filter
class CollectionTypeFilter(django_filters.FilterSet):
    name = django_filters.Filter(lookup_expr='icontains')

    class Meta:
        model = CollectionType
        exclude = ['uuid']


# CollectionCollectionTypeRelation filter
class CollectionCollectionTypeRelationFilter(django_filters.FilterSet):
    collection = django_filters.ModelMultipleChoiceFilter(
        queryset=Collection.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    type = django_filters.ModelMultipleChoiceFilter(
        queryset=CollectionType.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )

    class Meta:
        model = CollectionCollectionTypeRelation
        exclude = ['uuid']


# Catalogue filter
class CatalogueFilter(django_filters.FilterSet):
    name = django_filters.Filter(lookup_expr='icontains')

    class Meta:
        model = Catalogue
        fields = ['name', 'dataset']


# CatalogueYear filter
class CatalogueYearFilter(django_filters.FilterSet):
    year = django_filters.RangeFilter(widget=django_filters.widgets.RangeWidget())
    catalogue = django_filters.ModelMultipleChoiceFilter(
        queryset=Catalogue.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )

    class Meta:
        model = CatalogueYear
        exclude = ['uuid']


# Library filter
class LibraryFilter(django_filters.FilterSet):
    name = django_filters.Filter(lookup_expr='icontains')

    class Meta:
        model = Library
        exclude = ['uuid']


# Lot filter
class LotFilter(django_filters.FilterSet):
    collection__short_title = django_filters.Filter(field_name='collection__short_title', lookup_expr='icontains')

    collection = django_filters.ModelMultipleChoiceFilter(
        label="Collection",
        queryset=Collection.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Collection,
            search_fields=['short_title__icontains', 'full_title__icontains',
                           'preface_and_paratexts__icontains']
        ),
        # method='collection_filter'
    )
    category = django_filters.Filter(field_name='category__bookseller_category', lookup_expr='icontains')
    number_in_collection = django_filters.RangeFilter(widget=django_filters.widgets.RangeWidget())
    page_in_collection = django_filters.RangeFilter(widget=django_filters.widgets.RangeWidget())
    sales_price = django_filters.Filter(lookup_expr='icontains')
    lot_as_listed_in_collection = django_filters.Filter(lookup_expr='icontains')
    number_of_items = django_filters.Filter(label='Number of items', method='number_of_items_filter',
                                            widget=django_filters.widgets.RangeWidget())

    class Meta:
        model = Lot
        exclude = ['uuid']
        fields = [
            'collection__short_title',
            'collection',
            'number_in_collection',
            'page_in_collection',
            'sales_price',
            'lot_as_listed_in_collection',
            'index_in_collection',
            'category',
            'number_of_items',
        ]

    def number_of_items_filter(self, queryset, name, value):
        if any(value):
            queryset = queryset.annotate(num_items=Count('item'))
            if value[0]:
                queryset = queryset.filter(num_items__gte=value[0])
            if value[1]:
                queryset = queryset.filter(num_items__lte=value[1])
        return queryset


# PersonCollectionRelation filter
class PersonCollectionRelationFilter(django_filters.FilterSet):
    person = django_filters.ModelMultipleChoiceFilter(
        queryset=Person.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    collection = django_filters.ModelMultipleChoiceFilter(
        queryset=Collection.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    role = django_filters.ModelMultipleChoiceFilter(
        queryset=PersonCollectionRelationRole.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )

    class Meta:
        model = PersonCollectionRelation
        exclude = ['uuid']


# PersonCollectionRelationRole filter
class PersonCollectionRelationRoleFilter(django_filters.FilterSet):
    name = django_filters.Filter(lookup_expr='icontains')

    class Meta:
        model = PersonCollectionRelationRole
        exclude = ['uuid']


# PersonCatalogueRelation filter
class PersonCatalogueRelationFilter(django_filters.FilterSet):
    person = django_filters.ModelMultipleChoiceFilter(
        queryset=Person.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    catalogue = django_filters.ModelMultipleChoiceFilter(
        queryset=Catalogue.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )

    class Meta:
        model = PersonCatalogueRelation
        exclude = ['uuid']


# CollectionPlaceRelation filter
class CollectionPlaceRelationFilter(django_filters.FilterSet):
    collection = django_filters.ModelMultipleChoiceFilter(
        queryset=Collection.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    place = django_filters.ModelMultipleChoiceFilter(
        queryset=Place.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )

    class Meta:
        model = CollectionPlaceRelation
        exclude = ['uuid']


# Category filter
class CategoryFilter(django_filters.FilterSet):
    collection = django_filters.ModelMultipleChoiceFilter(
        queryset=Collection.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    bookseller_category = django_filters.Filter(lookup_expr='icontains')
    parisian_category = django_filters.ModelMultipleChoiceFilter(
        queryset=ParisianCategory.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )

    class Meta:
        model = Category
        exclude = ['uuid']


# ParisianCategory Filter
class ParisianCategoryFilter(django_filters.FilterSet):
    class Meta:
        model = ParisianCategory
        fields = {
            'name': ['icontains'],
            'description': ['icontains']
        }


# CollectionPlaceRelationType Filter
class CollectionPlaceRelationTypeFilter(django_filters.FilterSet):
    class Meta:
        model = CollectionPlaceRelationType
        fields = {
            'name': ['icontains'],
        }
