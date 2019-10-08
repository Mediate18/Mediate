import django_filters
from django_filters.widgets import RangeWidget
from django.db.models import Count
from django.forms import CheckboxInput
from django_select2.forms import ModelSelect2MultipleWidget, Select2MultipleWidget
from tagme.models import Tag
from .models import *
from catalogues.models import Catalogue
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
    book_format = django_filters.ModelMultipleChoiceFilter(
        queryset=BookFormat.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    catalogue = django_filters.ModelMultipleChoiceFilter(
        label="Catalogue",
        queryset=Catalogue.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Catalogue,
            search_fields=['short_title__icontains', 'full_title__icontains',
                           'preface_and_paratexts__icontains']
        ),
        method='catalogue_filter'
    )
    catalogue_publication_year = django_filters.RangeFilter(label="Catalogue publication year", widget=RangeWidget(),
                                                            field_name='lot__catalogue__year_of_publication')
    edition = django_filters.ModelMultipleChoiceFilter(
        queryset=Edition.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Edition,
            search_fields=['place__name__icontains', 'year__icontains', 'url__icontains']
        )
    )
    edition_isnull = django_filters.BooleanFilter(
        label="No associated edition",
        widget=CheckboxInput(),
        method='edition_isnull_filter'
    )
    edition_isempty = django_filters.BooleanFilter(
        label="Associated edition is empty",
        widget=CheckboxInput(),
        method='edition_isempty_filter'
    )
    edition_place = django_filters.ModelMultipleChoiceFilter(
        label="Stated place of publication",
        queryset=Place.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Place,
            search_fields=['name__icontains']
        ),
        method='edition_place_filter'
    )
    material_details = django_filters.ModelMultipleChoiceFilter(
        label="Material details",
        queryset=MaterialDetails.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
        method='material_details_filter'
    )
    tag = django_filters.ModelMultipleChoiceFilter(
        label='Tag',
        queryset=Tag.objects.all(),
        method='tag_filter',
        widget=ModelSelect2MultipleWidget(
            model=Tag,
            search_fields=['name__icontains'],
        ),
    )
    person = django_filters.ModelMultipleChoiceFilter(
        label='Person',
        queryset=Person.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Person,
            search_fields=['short_name__icontains']
        ),
        method='person_filter'
    )
    role = django_filters.ModelMultipleChoiceFilter(
        label='Role',
        queryset=PersonItemRelationRole.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=PersonItemRelationRole,
            search_fields=['name__icontains']
        ),
        method='role_filter'
    )
    person_role = django_filters.MultipleChoiceFilter(
        label='Person and Role',
        choices=[("{}|{}".format(rel['person'], rel['role']),
                  "{} - {}".format(rel['person__short_name'], rel['role__name']))
                 for rel in PersonItemRelation.objects.all()
                     .values('person', 'person__short_name', 'role', 'role__name').distinct()
                     .order_by('person__short_name')],
        method='person_role_filter',
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"})
    )

    class Meta:
        model = Item
        exclude = ['uuid']
        fields = [
            'short_title',
            'lot',
            'collection',
            'number_of_volumes',
            'book_format',
            'index_in_lot',
            'catalogue',
            'catalogue_publication_year',
            'edition',
            'edition_isnull',
            'edition_isempty',
            'edition_place',
            'sales_price',
            'material_details',
            'tag'
        ]

    def tag_filter(self, queryset, name, value):
        if value:
            return queryset.filter(tags__tag__in=value)
        return queryset

    def multiple_words_filter(self, queryset, name, value):
        return filter_multiple_words(self.filters[name].lookup_expr, queryset, name, value, wildcards=True)

    def material_details_filter(self, queryset, name, value):
        if value:
            return queryset.filter(itemmaterialdetailsrelation__material_details__in=value)
        else:
            return queryset

    def edition_isnull_filter(self, queryset, name, value):
        if value:
            return queryset.filter(edition__isnull=True)
        return queryset

    def edition_isempty_filter(self, queryset, name, value):
        if value:
            return queryset.filter(edition__year__isnull=True, edition__place__isnull=True)\
                .annotate(num_publishers=Count('edition__publisher')).filter(num_publishers=0)
        return queryset

    def edition_place_filter(self, queryset, name, value):
        if value:
            return queryset.filter(edition__place__in=value)
        return queryset

    def catalogue_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__catalogue__in=value)
        return queryset

    def person_filter(self, queryset, name, value):
        if value:
            return queryset.filter(personitemrelation__person__in=value).distinct()
        return queryset

    def role_filter(self, queryset, name, value):
        if value:
            return queryset.filter(personitemrelation__role__in=value).distinct()
        return queryset

    def person_role_filter(self, queryset, name, value):
        if value:
            for person_role in value:
                person_id, role_id = person_role.split('|')
                queryset = queryset.filter(personitemrelation__person__uuid=person_id, personitemrelation__role__uuid=role_id)
            return queryset
        return queryset


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


# Edition filter
class EditionFilter(django_filters.FilterSet):
    items = django_filters.Filter(name='items__short_title', lookup_expr='icontains')
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
    catalogue = django_filters.ModelMultipleChoiceFilter(
        label="Catalogue",
        queryset=Catalogue.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Catalogue,
            search_fields=['short_title__icontains', 'full_title__icontains',
                           'preface_and_paratexts__icontains']
        ),
        method='catalogue_filter'
    )
    number_of_items = django_filters.Filter(label='Number of items', method='number_of_items_filter',
                                            widget=django_filters.widgets.RangeWidget())

    class Meta:
        model = Edition
        exclude = ['uuid']

    def publisher_filter(self, queryset, name, value):
        if value:
            return queryset.filter(publisher__publisher__in=value)
        return queryset

    def number_of_items_filter(self, queryset, name, value):
        if value[0]:
            queryset = queryset.annotate(num_items=Count('items')).filter(num_items__gte=value[0])
        if value[1]:
            queryset = queryset.annotate(num_items=Count('items')).filter(num_items__lte=value[1])
        return queryset

    def catalogue_filter(self, queryset, name, value):
        if value:
            return queryset.filter(items__lot__catalogue__in=value)
        return queryset

# Publisher filter
class PublisherFilter(django_filters.FilterSet):
    publisher = django_filters.Filter(name='publisher__short_name', lookup_expr='icontains')
    edition = django_filters.Filter(name='edition__item__short_title', lookup_expr='icontains')
    edition__place = django_filters.ModelMultipleChoiceFilter(
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


