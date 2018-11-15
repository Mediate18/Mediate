import django_filters
from django_select2.forms import Select2MultipleWidget
from .models import *
from mediate.tools import filter_multiple_words


# Catalogue filter
class CatalogueFilter(django_filters.FilterSet):
    short_title = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    full_title = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    preface_and_paratexts = django_filters.Filter(lookup_expr='icontains')
    type = django_filters.ModelMultipleChoiceFilter(
        queryset=CatalogueType.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    terminus_post_quem = django_filters.BooleanFilter(widget=django_filters.widgets.BooleanWidget())
    collection = django_filters.Filter(name='collection__name', lookup_expr='icontains')
    notes = django_filters.Filter(lookup_expr='icontains')
    bibliography = django_filters.Filter(lookup_expr='icontains')

    class Meta:
        model = Catalogue
        fields = "__all__"
        exclude = ['transcription', 'uuid']

    def multiple_words_filter(self, queryset, name, value):
        return filter_multiple_words(self.filters[name].lookup_expr, queryset, name, value)



# CatalogueHeldBy filter
class CatalogueHeldByFilter(django_filters.FilterSet):
    class Meta:
        model = CatalogueHeldBy
        fields = "__all__"


# CatalogueType filter
class CatalogueTypeFilter(django_filters.FilterSet):
    class Meta:
        model = CatalogueType
        fields = "__all__"


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
        fields = "__all__"


# Library filter
class LibraryFilter(django_filters.FilterSet):
    class Meta:
        model = Library
        fields = "__all__"


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
        fields = "__all__"


# PersonCatalogueRelationRole filter
class PersonCatalogueRelationRoleFilter(django_filters.FilterSet):
    class Meta:
        model = PersonCatalogueRelationRole
        fields = "__all__"


# PersonCollectionRelation filter
class PersonCollectionRelationFilter(django_filters.FilterSet):
    class Meta:
        model = PersonCollectionRelation
        fields = "__all__"


# Category filter
class CategoryFilter(django_filters.FilterSet):
    class Meta:
        model = Category
        exclude = ['uuid']
