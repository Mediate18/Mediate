import django_filters
from django_select2.forms import Select2MultipleWidget
from .models import *
from mediate.tools import filter_multiple_words


# Catalogue filter
class CatalogueFilter(django_filters.FilterSet):
    short_title = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    full_title = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    preface_and_paratexts = django_filters.Filter(lookup_expr='icontains')
    types = django_filters.ModelMultipleChoiceFilter(
        label='Types',
        queryset=CatalogueType.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
        method='catalogue_types_filter'
    )
    terminus_post_quem = django_filters.BooleanFilter(widget=django_filters.widgets.BooleanWidget())
    collection = django_filters.Filter(name='collection__name', lookup_expr='icontains')
    notes = django_filters.Filter(lookup_expr='icontains')
    bibliography = django_filters.Filter(lookup_expr='icontains')

    class Meta:
        model = Catalogue
        fields = [
            'short_title',
            'full_title',
            'types',
            'preface_and_paratexts',
            'year_of_publication',
            'terminus_post_quem',
            'notes',
            'bibliography',
            'collection'
        ]

    def multiple_words_filter(self, queryset, name, value):
        return filter_multiple_words(self.filters[name].lookup_expr, queryset, name, value)

    def catalogue_types_filter(self, queryset, name, value):
        if value:
            return queryset.filter(cataloguecataloguetyperelation__type__in=value)
        else:
            return queryset


# CatalogueHeldBy filter
class CatalogueHeldByFilter(django_filters.FilterSet):
    class Meta:
        model = CatalogueHeldBy
        exclude = ['uuid']


# CatalogueType filter
class CatalogueTypeFilter(django_filters.FilterSet):
    class Meta:
        model = CatalogueType
        exclude = ['uuid']


# CatalogueCatalogueTypeRelation filter
class CatalogueCatalogueTypeRelationFilter(django_filters.FilterSet):
    catalogue = django_filters.ModelMultipleChoiceFilter(
        queryset=Catalogue.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    type = django_filters.ModelMultipleChoiceFilter(
        queryset=CatalogueType.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )

    class Meta:
        model = CatalogueCatalogueTypeRelation
        exclude = ['uuid']


# Collection filter
class CollectionFilter(django_filters.FilterSet):
    name = django_filters.Filter(lookup_expr='icontains')

    class Meta:
        model = Collection
        fields = ['name']


# CollectionYear filter
class CollectionYearFilter(django_filters.FilterSet):
    class Meta:
        model = CollectionYear
        exclude = ['uuid']


# Library filter
class LibraryFilter(django_filters.FilterSet):
    class Meta:
        model = Library
        exclude = ['uuid']


# Lot filter
class LotFilter(django_filters.FilterSet):
    catalogue = django_filters.Filter(name='catalogue__short_title', lookup_expr='icontains')
    category = django_filters.Filter(name='category__bookseller_category', lookup_expr='icontains')
    number_in_catalogue = django_filters.RangeFilter(widget=django_filters.widgets.RangeWidget())
    page_in_catalogue = django_filters.RangeFilter(widget=django_filters.widgets.RangeWidget())
    sales_price = django_filters.Filter(lookup_expr='icontains')
    lot_as_listed_in_catalogue = django_filters.Filter(lookup_expr='icontains')

    class Meta:
        model = Lot
        exclude = ['uuid']


# PersonCatalogueRelation filter
class PersonCatalogueRelationFilter(django_filters.FilterSet):
    class Meta:
        model = PersonCatalogueRelation
        exclude = ['uuid']


# PersonCatalogueRelationRole filter
class PersonCatalogueRelationRoleFilter(django_filters.FilterSet):
    class Meta:
        model = PersonCatalogueRelationRole
        exclude = ['uuid']


# PersonCollectionRelation filter
class PersonCollectionRelationFilter(django_filters.FilterSet):
    class Meta:
        model = PersonCollectionRelation
        exclude = ['uuid']


# Category filter
class CategoryFilter(django_filters.FilterSet):
    class Meta:
        model = Category
        exclude = ['uuid']
