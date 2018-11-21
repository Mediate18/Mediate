import django_filters
from django_filters.widgets import RangeWidget, BooleanWidget
from django_select2.forms import ModelSelect2MultipleWidget, Select2MultipleWidget
from tagging.models import Tag, TaggedItem
from .models import *
from mediate.tools import filter_multiple_words
from viapy.api import ViafAPI


# BookFormat filter
class BookFormatFilter(django_filters.FilterSet):
    class Meta:
        model = BookFormat
        exclude = ['uuid']


# Item filter
class ItemFilter(django_filters.FilterSet):
    short_title = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    lot = django_filters.Filter(name='lot__lot_as_listed_in_catalogue', lookup_expr='icontains')
    sales_price = django_filters.Filter(name='lot__sales_price', lookup_expr='icontains')
    collection = django_filters.Filter(name='collection__name', lookup_expr='icontains')
    number_of_volumes = django_filters.Filter(lookup_expr='icontains')
    tag = django_filters.ModelMultipleChoiceFilter(
        label='Tag',
        queryset=Tag.objects.all(),
        method='tag_filter',
        widget=ModelSelect2MultipleWidget(
            model=Tag,
            search_fields=['name__icontains'],
        ),
    )

    class Meta:
        model = Item
        exclude = ['uuid']

    def tag_filter(self, queryset, name, value):
        if value:
            return TaggedItem.objects.get_by_model(queryset, value)
        return queryset

    def multiple_words_filter(self, queryset, name, value):
        return filter_multiple_words(self.filters[name].lookup_expr, queryset, name, value)


# ItemAuthor filter
class ItemAuthorFilter(django_filters.FilterSet):
    item = django_filters.Filter(name='item__short_title', lookup_expr='icontains')

    class Meta:
        model = ItemAuthor
        exclude = ['uuid']


# ItemItemTypeRelation filter
class ItemItemTypeRelationFilter(django_filters.FilterSet):
    item = django_filters.Filter(name='item__short_title', lookup_expr='icontains')

    class Meta:
        model = ItemItemTypeRelation
        exclude = ['uuid']


# ItemLanguageRelation filter
class ItemLanguageRelationFilter(django_filters.FilterSet):
    item = django_filters.Filter(name='item__short_title', lookup_expr='icontains')

    class Meta:
        model = ItemLanguageRelation
        exclude = ['uuid']


# ItemMaterialDetailsRelation filter
class ItemMaterialDetailsRelationFilter(django_filters.FilterSet):
    item = django_filters.Filter(name='item__short_title', lookup_expr='icontains')

    class Meta:
        model = ItemMaterialDetailsRelation
        exclude = ['uuid']


# ItemType filter
class ItemTypeFilter(django_filters.FilterSet):
    class Meta:
        model = ItemType
        exclude = ['uuid']


# ItemWorkRelation filter
class ItemWorkRelationFilter(django_filters.FilterSet):
    item = django_filters.Filter(name='item__short_title', lookup_expr='icontains')

    class Meta:
        model = ItemWorkRelation
        exclude = ['uuid']


# Language filter
class LanguageFilter(django_filters.FilterSet):
    class Meta:
        model = Language
        exclude = ['uuid']


# MaterialDetails filter
class MaterialDetailsFilter(django_filters.FilterSet):
    class Meta:
        model = MaterialDetails
        exclude = ['uuid']


# PersonItemRelation filter
class PersonItemRelationFilter(django_filters.FilterSet):
    item = django_filters.Filter(name='item__short_title', lookup_expr='icontains')

    class Meta:
        model = PersonItemRelation
        exclude = ['uuid']


# PersonItemRelationRole filter
class PersonItemRelationRoleFilter(django_filters.FilterSet):
    class Meta:
        model = PersonItemRelationRole
        exclude = ['uuid']


# Manifestation filter
class ManifestationFilter(django_filters.FilterSet):
    item = django_filters.Filter(name='item__short_title', lookup_expr='icontains')
    year = django_filters.RangeFilter(widget=RangeWidget())
    year_tag = django_filters.Filter(lookup_expr='icontains')
    place = django_filters.ModelMultipleChoiceFilter(
        queryset=Place.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    url = django_filters.Filter(lookup_expr='icontains')
    publisher = django_filters.ModelMultipleChoiceFilter(
        label='Publisher',
        queryset=Person.objects.all(),
        method='publisher_filter',
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )

    class Meta:
        model = Manifestation
        exclude = ['uuid']

    def publisher_filter(self, queryset, name, value):
        if value:
            return queryset.filter(publisher__publisher__in=value)
        return queryset

# Publisher filter
class PublisherFilter(django_filters.FilterSet):
    publisher = django_filters.Filter(name='publisher__short_name', lookup_expr='icontains')
    manifestation = django_filters.Filter(name='manifestation__item__short_title', lookup_expr='icontains')
    manifestation__place = django_filters.ModelMultipleChoiceFilter(
        queryset=Place.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )

    class Meta:
        model = Publisher
        exclude = ['uuid']


# Subject filter
class SubjectFilter(django_filters.FilterSet):
    class Meta:
        model = Subject
        exclude = ['uuid']


# Work filter
class WorkFilter(django_filters.FilterSet):
    title = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    viaf_id = django_filters.Filter(method='viaf_id_filter')

    class Meta:
        model = Work
        exclude = ['uuid']

    def viaf_id_filter(self, queryset, name, value):
        if value:
            return queryset.filter(viaf_id=ViafAPI.uri_base+"/"+value)
        return queryset

    def multiple_words_filter(self, queryset, name, value):
        return filter_multiple_words(self.filters[name].lookup_expr, queryset, name, value)


# WorkAuthor filter
class WorkAuthorFilter(django_filters.FilterSet):
    class Meta:
        model = WorkAuthor
        exclude = ['uuid']


# WorkSubject filter
class WorkSubjectFilter(django_filters.FilterSet):
    class Meta:
        model = WorkSubject
        exclude = ['uuid']


