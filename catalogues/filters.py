import django_filters
from django_select2.forms import Select2MultipleWidget
from .models import *


# Catalogue filter
class CatalogueFilter(django_filters.FilterSet):
    short_title = django_filters.Filter(lookup_expr='icontains')
    full_title = django_filters.Filter(lookup_expr='icontains')
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
    class Meta:
        model = Collection
        fields = "__all__"


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

    class Meta:
        model = Lot
        fields = "__all__"


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


