import django_filters
from django_filters.widgets import RangeWidget
from django.db.models import Count
from django.forms import CheckboxInput
from django_select2.forms import ModelSelect2MultipleWidget, Select2MultipleWidget, HeavySelect2MultipleWidget
from tagme.models import Tag
from .models import *
from persons.models import Country, Profession, Religion
from catalogues.models import Catalogue, ParisianCategory, PersonCatalogueRelation
from mediate.tools import filter_multiple_words
from viapy.api import ViafAPI

from django.urls import reverse_lazy


# BookFormat filter
class BookFormatFilter(django_filters.FilterSet):
    class Meta:
        model = BookFormat
        exclude = ['uuid']


# Item filter
class ItemFilter(django_filters.FilterSet):
    short_title = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    lot = django_filters.Filter(name='lot__lot_as_listed_in_catalogue', lookup_expr='icontains')
    number_of_volumes = django_filters.Filter(lookup_expr='icontains')
    book_format = django_filters.ModelMultipleChoiceFilter(
        queryset=BookFormat.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    non_book = django_filters.BooleanFilter(
        label="Include non-book items",
        widget=CheckboxInput,
        method='include_non_book_items_filter'
    )
    item_type = django_filters.ModelMultipleChoiceFilter(
        label="Item Type",
        queryset=ItemType.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=ItemType,
            search_fields=['name__icontains']
        ),
        method='item_type_filter'
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
    parisian_category = django_filters.ModelMultipleChoiceFilter(
        label="Parisian category",
        queryset=ParisianCategory.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=ParisianCategory,
            search_fields=['name__icontains', 'description__icontains']
        ),
        method='parisian_category_filter'
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
    edition_year = django_filters.RangeFilter(label="Date of publication", widget=RangeWidget(),
                                                            field_name='edition__year')
    edition_year_tag = django_filters.Filter(
        label="Date of publication tag",
        name='edition__year_tag',
        lookup_expr='icontains'
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
    exclude_person = django_filters.ModelMultipleChoiceFilter(
        label='Not related person',
        queryset=Person.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Person,
            search_fields=['short_name__icontains']
        ),
        method='exclude_person_filter'
    )
    person_role = django_filters.MultipleChoiceFilter(
        label='Person and Role',
        choices=[],
        method='person_role_filter',
        widget=HeavySelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            data_view='personroleautoresponse'
        )
    )
    owner_gender = django_filters.ChoiceFilter(
        label="Owner gender",
        choices=Person.SEX_CHOICES,
        method='owner_gender_filter'
    )
    owner_country_of_birth = django_filters.ModelMultipleChoiceFilter(
        label="Owner country of birth",
        queryset=Country.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Country,
            search_fields=['name__icontains']
        ),
        method='owner_country_of_birth_filter'
    )
    owner_country_of_death = django_filters.ModelMultipleChoiceFilter(
        label="Owner country of death",
        queryset=Country.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Country,
            search_fields=['name__icontains']
        ),
        method='owner_country_of_death_filter'
    )
    owner_country_of_residence = django_filters.ModelMultipleChoiceFilter(
        label="Owner country of residence",
        queryset=Country.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Country,
            search_fields=['name__icontains']
        ),
        method='owner_country_of_residence_filter'
    )
    owner_profession = django_filters.ModelMultipleChoiceFilter(
        label="Owner profession",
        queryset=Profession.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Profession,
            search_fields=['name__icontains']
        ),
        method='owner_profession_filter'
    )
    owner_religion = django_filters.ModelMultipleChoiceFilter(
        label="Ovner religion",
        queryset=Religion.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Religion,
            search_fields=['name__icontains']
        ),
        method='owner_religion_filter'
    )
    language = django_filters.ModelMultipleChoiceFilter(
        label='Language',
        queryset=Language.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Language,
            search_fields=['name__icontains', 'language_code_2char__iexact', 'language_code_3char__iexact']
        ),
        method='language_filter'
    )
    catalogue_country_of_publication = django_filters.ModelMultipleChoiceFilter(
        label="Catalogue country of publication",
        queryset=Country.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Country,
            search_fields=['name__icontains']
        ),
        method='catalogue_country_of_publication_filter'
    )
    catalogue_city_of_publication = django_filters.ModelMultipleChoiceFilter(
        label="Catalogue city of publication",
        queryset=Place.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Place,
            search_fields=['name__icontains']
        ),
        method='catalogue_city_of_publication_filter'
    )
    catalogue_tag = django_filters.ModelMultipleChoiceFilter(
        label="Catalogue tag",
        queryset=Tag.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Tag,
            search_fields=['namespace__icontains', 'name__icontains', 'value__icontains']
        ),
        method='catalogue_tag_filter'
    )

    class Meta:
        model = Item
        exclude = ['uuid']
        fields = [
            'short_title',
            'lot',
            'number_of_volumes',
            'book_format',
            'non_book',
            'item_type',
            'catalogue',
            'catalogue_publication_year',
            'parisian_category',
            'edition_isnull',
            'edition_isempty',
            'edition_place',
            'edition_year',
            'edition_year_tag',
            'material_details',
            'tag',
            'catalogue_country_of_publication',
            'catalogue_city_of_publication',
            'catalogue_tag',
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

    def include_non_book_items_filter(self, queryset, name, value):
        """
        If value is True Items with ItemType containing 'book' are included.
        Those Items are excluded by default.
        :param queryset: the filter queryset
        :param name: the name of the field
        :param value: the value of field
        :return: the filter queryset
        """
        if value:
            return queryset
        return queryset.exclude(non_book=True)

    def item_type_filter(self, queryset, name, value):
        if value:
            return queryset.filter(itemitemtyperelation__type__name__in=value)
        return queryset

    def parisian_category_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__category__parisian_category__in=value)
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

    def exclude_person_filter(self, queryset, name, value):
        if value:
            return queryset.exclude(personitemrelation__person__in=value).distinct()
        return queryset

    def person_role_filter(self, queryset, name, value):
        if value:
            for person_role in value:
                person_id, role_id = person_role.split('|')
                queryset = queryset.filter(personitemrelation__person__uuid=person_id, personitemrelation__role__uuid=role_id)
            return queryset
        return queryset

    def language_filter(self, queryset, name, value):
        if value:
            return queryset.filter(languages__language__in=value)
        return queryset

    def owner_gender_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__catalogue__personcataloguerelation__in=
                                   PersonCatalogueRelation.objects.filter(role__name__iexact='owner', person__sex=value))
        return queryset

    def owner_country_of_birth_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__catalogue__personcataloguerelation__in=PersonCatalogueRelation.objects.filter(
                role__name__iexact='owner', person__city_of_birth__country__in=value))
        return queryset

    def owner_country_of_death_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__catalogue__personcataloguerelation__in=PersonCatalogueRelation.objects.filter(
                role__name__iexact='owner', person__city_of_death__country__in=value))
        return queryset

    def owner_country_of_residence_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__catalogue__personcataloguerelation__in=PersonCatalogueRelation.objects.filter(
                role__name__iexact='owner', person__residence__place__country__in=value))
        return queryset

    def owner_profession_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__catalogue__personcataloguerelation__in=PersonCatalogueRelation.objects.filter(
                role__name__iexact='owner', person__personprofession__profession__in=value))
        return queryset

    def owner_religion_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__catalogue__personcataloguerelation__in=PersonCatalogueRelation.objects.filter(
                role__name__iexact='owner', person__religiousaffiliation__religion__in=value))
        return queryset

    def catalogue_country_of_publication_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__catalogue__related_places__place__country__in=value).distinct()
        return queryset

    def catalogue_city_of_publication_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__catalogue__related_places__place__in=value).distinct()
        return queryset

    def catalogue_tag_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__catalogue__tags__tag__in=value).distinct()
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
    url = django_filters.BooleanFilter(
        label="Has URL",
        method='has_url_filter'
    )
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
    language = django_filters.ModelMultipleChoiceFilter(
        label='Language',
        queryset=Language.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Language,
            search_fields=['name__icontains', 'language_code_2char__iexact', 'language_code_3char__iexact']
        ),
        method='language_filter'
    )
    book_format = django_filters.ModelMultipleChoiceFilter(
        label="Book format",
        queryset=BookFormat.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=BookFormat,
            search_fields=['name__icontains']
        ),
        method='book_format_filter'
    )

    class Meta:
        model = Edition
        exclude = ['uuid']

    def has_url_filter(self, queryset, name, value):
        print("value", value, str(value), type(value))
        if value:
            return queryset.exclude(url__exact="")
        else:
            return queryset.filter(url__exact="")

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

    def language_filter(self, queryset, name, value):
        if value:
            return queryset.filter(items__languages__language__in=value)
        return queryset

    def book_format_filter(self, queryset, name, value):
        if value:
            return queryset.filter(items__book_format__in=value)
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


