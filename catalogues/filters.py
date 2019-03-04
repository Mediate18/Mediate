import django_filters
from django.db.models import Count
from django_select2.forms import Select2MultipleWidget
from .models import *
from mediate.tools import filter_multiple_words
from persons.models import Profession, Religion


# Catalogue filter
class CatalogueFilter(django_filters.FilterSet):
    short_title = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    full_title = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    types = django_filters.ModelMultipleChoiceFilter(
        label='Types',
        queryset=CatalogueType.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
        method='catalogue_types_filter'
    )
    year_of_publication = django_filters.RangeFilter(widget=django_filters.widgets.RangeWidget())
    terminus_post_quem = django_filters.BooleanFilter(widget=django_filters.widgets.BooleanWidget())
    number_of_items = django_filters.Filter(label='Number of items', method='number_of_items_filter',
                                            widget=django_filters.widgets.RangeWidget())
    number_of_lots = django_filters.Filter(label='Number of lots', method='number_of_lots_filter',
                                            widget=django_filters.widgets.RangeWidget())
    publisher = django_filters.ModelMultipleChoiceFilter(
        label="Publisher",
        queryset=Person.objects.filter(personcataloguerelation__role__name='publisher'),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
        field_name='personcataloguerelation__person',
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
    owner_profession = django_filters.ModelMultipleChoiceFilter(
        label="Owner religion",
        queryset=Religion.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        method='owner_religion_filter'
    )

    class Meta:
        model = Catalogue
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

    def catalogue_types_filter(self, queryset, name, value):
        if value:
            return queryset.filter(cataloguecataloguetyperelation__type__in=value)
        else:
            return queryset

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
            return queryset.filter(personcataloguerelation__role__name='owner',
                                   personcataloguerelation__person__sex__in=value)
        return queryset

    def owner_profession_filter(self, queryset, name, value):
        if value:
            return queryset.filter(personcataloguerelation__role__name='owner',
                                   personcataloguerelation__person__personprofession__profession__in=value)
        return queryset

    def owner_religion_filter(self, queryset, name, value):
        if value:
            return queryset.filter(personcataloguerelation__role__name='owner',
                                   personcataloguerelation__person__religiousaffiliation__religion__in=value)
        return queryset


# CatalogueHeldBy filter
class CatalogueHeldByFilter(django_filters.FilterSet):
    library = django_filters.ModelMultipleChoiceFilter(
        queryset=Library.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
    )
    catalogue = django_filters.ModelMultipleChoiceFilter(
        queryset=Catalogue.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
    )

    class Meta:
        model = CatalogueHeldBy
        exclude = ['uuid']


# CatalogueType filter
class CatalogueTypeFilter(django_filters.FilterSet):
    name = django_filters.Filter(lookup_expr='icontains')

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
    year = django_filters.RangeFilter(widget=django_filters.widgets.RangeWidget())
    collection = django_filters.ModelMultipleChoiceFilter(
        queryset=Collection.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )

    class Meta:
        model = CollectionYear
        exclude = ['uuid']


# Library filter
class LibraryFilter(django_filters.FilterSet):
    name = django_filters.Filter(lookup_expr='icontains')

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
    number_of_items = django_filters.Filter(label='Number of items', method='number_of_items_filter',
                                            widget=django_filters.widgets.RangeWidget())

    class Meta:
        model = Lot
        exclude = ['uuid']

    def number_of_items_filter(self, queryset, name, value):
        if any(value):
            queryset = queryset.annotate(num_items=Count('item'))
            if value[0]:
                queryset = queryset.filter(num_items__gte=value[0])
            if value[1]:
                queryset = queryset.filter(num_items__lte=value[1])
        return queryset


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
    role = django_filters.ModelMultipleChoiceFilter(
        queryset=PersonCatalogueRelationRole.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )

    class Meta:
        model = PersonCatalogueRelation
        exclude = ['uuid']


# PersonCatalogueRelationRole filter
class PersonCatalogueRelationRoleFilter(django_filters.FilterSet):
    name = django_filters.Filter(lookup_expr='icontains')

    class Meta:
        model = PersonCatalogueRelationRole
        exclude = ['uuid']


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

    class Meta:
        model = PersonCollectionRelation
        exclude = ['uuid']


# Category filter
class CategoryFilter(django_filters.FilterSet):
    catalogue = django_filters.ModelMultipleChoiceFilter(
        queryset=Catalogue.objects.all(),
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
