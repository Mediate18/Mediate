import django_filters
from django_filters.widgets import RangeWidget
from django.db.models import Count, Q, QuerySet
from django.forms import CheckboxInput
from django_select2.forms import ModelSelect2MultipleWidget, Select2MultipleWidget, HeavySelect2MultipleWidget
from tagme.models import Tag
from .models import *
from persons.models import Country, Profession, Religion
from catalogues.models import Collection, ParisianCategory, PersonCollectionRelation
from catalogues.views.views import get_collections_for_session
from mediate.tools import filter_multiple_words
from mediate.filters import QBasedFilterset, RangeFilterQ, MultipleChoiceFilterQWithExtraLookups, \
    ModelMultipleChoiceFilterQ

from django.urls import reverse_lazy


# BookFormat filter
class BookFormatFilter(django_filters.FilterSet):
    class Meta:
        model = BookFormat
        exclude = ['uuid']


class PersonRoleMultipleChoiceField(django_filters.fields.MultipleChoiceField):
    def valid_value(self, value):
        try:
            person_uuid, role_uuid = value.split('|')
            uuid.UUID(person_uuid)
            uuid.UUID(role_uuid)
            return True
        except ValueError:
            return False


class ItemTagRankingFilter(QBasedFilterset):
    name = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    value = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    collection = ModelMultipleChoiceFilterQ(
        label="Collection",
        queryset=Collection.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Collection,
            search_fields=['short_title__icontains']
        ),
        field_name='taggedentity__items__lot__collection',
        lookup_expr='in'
    )
    collection_publication_year = RangeFilterQ(
        label="Collection publication year",
        widget=RangeWidget(),
        field_name='taggedentity__items__lot__collection__year_of_publication'
    )
    collection_country_of_publication = ModelMultipleChoiceFilterQ(
        label="Collection country of publication",
        queryset=Country.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Country,
            search_fields=['name__icontains']
        ),
        method='collection_country_of_publication_filter'
    )
    collection_tag = ModelMultipleChoiceFilterQ(
        label="Collection tag",
        queryset=Tag.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Tag,
            search_fields=['namespace__icontains', 'name__icontains', 'value__icontains']
        ),
        method='collection_tag_filter'
    )
    collection_owner_religion = ModelMultipleChoiceFilterQ(
        label="Collection owner religion",
        queryset=Religion.objects.all().order_by('name'),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        method='collection_owner_religion_filter'
    )

    class Meta:
        model = Tag
        exclude = ['namespace', 'uuid']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.request = request

    # Override method
    @property
    def qs(self):
        qs = super().qs
        self._qs = qs.distinct() \
            .annotate(item_count=Count('taggedentity__items',
                                       filter=Q(taggedentity__items__non_book=False,
                                                taggedentity__items__lot__collection__in=
                                                get_collections_for_session(self.request)),
                                       distinct=True)) \
            .order_by('-item_count')
        return self._qs

    def multiple_words_filter(self, queryset, name, value):
        return filter_multiple_words(self.filters[name].lookup_expr, queryset, name, value, wildcards=True)

    def collection_country_of_publication_filter(self, q, name, value):
        if value:
            q &= Q(taggedentity__items__lot__collection__related_places__type__name='publication',
                   taggedentity__items__lot__collection__related_places__place__country__in=value)
        return q

    def collection_tag_filter(self, q, name, value):
        if value:
            q &= Q(taggedentity__items__lot__collection__tags__tag__in=value)
        return q

    def collection_owner_religion_filter(self, q, name, value):
        if value:
            q &= Q(taggedentity__items__lot__collection__personcollectionrelation__role__name='owner',
              taggedentity__items__lot__collection__personcollectionrelation__person__religiousaffiliation__religion__in=value)
        return q


# Item filter
class ItemFilter(django_filters.FilterSet):
    short_title = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    lot = django_filters.Filter(field_name='lot__lot_as_listed_in_collection', lookup_expr='icontains')
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
    collection = django_filters.ModelMultipleChoiceFilter(
        label="Collection",
        queryset=Collection.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Collection,
            search_fields=['short_title__icontains', 'full_title__icontains',
                           'preface_and_paratexts__icontains']
        ),
        method='collection_filter'
    )
    collection_publication_year = django_filters.RangeFilter(label="Collection publication year", widget=RangeWidget(),
                                                            field_name='lot__collection__year_of_publication')
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
    lot_isnull = django_filters.BooleanFilter(
        label="No associated lot",
        widget=CheckboxInput(),
        method='lot_isnull_filter'
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
    real_place_of_publication = django_filters.ModelMultipleChoiceFilter(
        label="Real place of publication",
        queryset=Place.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Place,
            search_fields=['name__icontains']
        ),
        method='real_place_of_publication_filter'
    )
    edition_year = django_filters.RangeFilter(label="Date of publication", widget=RangeWidget(),
                                              field_name='edition__year', method='year_filter')
    edition_year_tag = django_filters.Filter(
        label="Date of publication tag",
        field_name='edition__year_tag',
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
    sex = django_filters.MultipleChoiceFilter(
        label='Person gender',
        choices=Person.SEX_CHOICES,
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
        method='person_sex_filter'
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
    # Override the field_class (with valid_value method)
    person_role.field_class= PersonRoleMultipleChoiceField

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
    publisher = django_filters.ModelMultipleChoiceFilter(
        label="Publisher",
        queryset=Person.objects.filter(publisher__isnull=False).distinct(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Person,
            queryset=Person.objects.filter(publisher__isnull=False).distinct(),
            search_fields=['short_name__icontains', 'surname__icontains', 'first_names__icontains']
        ),
        field_name='edition__publisher__publisher'
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
    collection_country_of_publication = django_filters.ModelMultipleChoiceFilter(
        label="Collection country of publication",
        queryset=Country.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Country,
            search_fields=['name__icontains']
        ),
        method='collection_country_of_publication_filter'
    )
    collection_city_of_publication = django_filters.ModelMultipleChoiceFilter(
        label="Collection city of publication",
        queryset=Place.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Place,
            search_fields=['name__icontains']
        ),
        method='collection_city_of_publication_filter'
    )
    collection_tag = django_filters.ModelMultipleChoiceFilter(
        label="Collection tag",
        queryset=Tag.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Tag,
            search_fields=['namespace__icontains', 'name__icontains', 'value__icontains']
        ),
        method='collection_tag_filter'
    )
    works = django_filters.ModelMultipleChoiceFilter(
        queryset=Work.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Work,
            search_fields=['title__icontains', 'viaf_id__icontains']
        ),
        method='works_filter'
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
            'collection',
            'collection_publication_year',
            'parisian_category',
            'lot_isnull',
            'edition_isnull',
            'edition_isempty',
            'edition_place',
            'real_place_of_publication',
            'edition_year',
            'edition_year_tag',
            'material_details',
            'tag',
            'collection_country_of_publication',
            'collection_city_of_publication',
            'collection_tag',
        ]

    def __init__(self, data=None, *args, **kwargs):
        self.pass_selected_choices_to_person_role_filter(data)
        super().__init__(data, *args, **kwargs)

    def pass_selected_choices_to_person_role_filter(self, data):
        """Passes the selected choices are in field on the result page"""
        if data is not None:
            person_role_field = self.base_filters.get('person_role')
            person_roles = data.getlist('person_role')
            person_role_choices = []
            for person_role in person_roles:
                person_id, role_id = person_role.split('|')
                person_name = Person.objects.get(uuid=person_id).short_name
                role_name = PersonItemRelationRole.objects.get(uuid=role_id).name
                person_role_choices.append((person_role,"{} - {}".format(person_name, role_name)))
            person_role_field.extra['choices'] = person_role_choices

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
        return queryset.filter(Q(non_book=False) |
                               Q(itemitemtyperelation__type__name="maps and charts (loose)") |
                               Q(itemitemtyperelation__type__name="prints and etchings (loose)"))

    def item_type_filter(self, queryset, name, value):
        if value:
            return queryset.filter(itemitemtyperelation__type__name__in=value)
        return queryset

    def parisian_category_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__category__parisian_category__in=value)
        return queryset

    def lot_isnull_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__isnull=True)
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

    def real_place_of_publication_filter(self, queryset, name, value):
        if value:
            return queryset.filter(edition__publicationplace__place__in=value)
        return queryset

    def year_filter(self, queryset, name, value):
        if value:
            if value.start and not value.stop:
                q = Q(edition__year_start__gte=value.start) | Q(edition__year_end__gte=value.start)
            elif value.stop and not value.start:
                q = Q(edition__year_start__lte=value.stop)
            else:  # value.start and value.end
                # Either year_start  within value range
                # or     year_end    within value range
                # or     value range inside range of year_start to year_end
                q = (Q(edition__year_start__gte=value.start) & Q(edition__year_start__lte=value.stop)) \
                    | (Q(edition__year_end__gte=value.start) & Q(edition__year_end__lte=value.stop)) \
                    | (Q(edition__year_start__lte=value.start) & Q(edition__year_end__gte=value.stop))

            return queryset.filter(q)
        return queryset

    def collection_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__collection__in=value)
        return queryset

    def person_filter(self, queryset, name, value):
        if value:
            return queryset.filter(personitemrelation__person__in=value).distinct()
        return queryset

    def person_sex_filter(self, queryset, name, value):
        if value:
            return queryset.filter(personitemrelation__person__sex__in=value).distinct()
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
            return queryset.filter(lot__collection__personcollectionrelation__in=
                                   PersonCollectionRelation.objects.filter(role__name__iexact='owner', person__sex=value))
        return queryset

    def owner_country_of_birth_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__collection__personcollectionrelation__in=PersonCollectionRelation.objects.filter(
                role__name__iexact='owner', person__city_of_birth__country__in=value))
        return queryset

    def owner_country_of_death_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__collection__personcollectionrelation__in=PersonCollectionRelation.objects.filter(
                role__name__iexact='owner', person__city_of_death__country__in=value))
        return queryset

    def owner_country_of_residence_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__collection__personcollectionrelation__in=PersonCollectionRelation.objects.filter(
                role__name__iexact='owner', person__residence__place__country__in=value))
        return queryset

    def owner_profession_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__collection__personcollectionrelation__in=PersonCollectionRelation.objects.filter(
                role__name__iexact='owner', person__personprofession__profession__in=value))
        return queryset

    def owner_religion_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__collection__personcollectionrelation__in=PersonCollectionRelation.objects.filter(
                role__name__iexact='owner', person__religiousaffiliation__religion__in=value))
        return queryset

    def collection_country_of_publication_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__collection__related_places__place__country__in=value).distinct()
        return queryset

    def collection_city_of_publication_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__collection__related_places__place__in=value).distinct()
        return queryset

    def collection_tag_filter(self, queryset, name, value):
        if value:
            return queryset.filter(lot__collection__tags__tag__in=value).distinct()
        return queryset

    def works_filter(self, queryset, name, value):
        if value:
            return queryset.filter(works__work__in=value).distinct()
        return queryset


# ItemAuthor filter
class ItemAuthorFilter(django_filters.FilterSet):
    item = django_filters.Filter(field_name='item__short_title', lookup_expr='icontains')

    class Meta:
        model = ItemAuthor
        exclude = ['uuid']


# ItemItemTypeRelation filter
class ItemItemTypeRelationFilter(django_filters.FilterSet):
    item = django_filters.Filter(field_name='item__short_title', lookup_expr='icontains')

    class Meta:
        model = ItemItemTypeRelation
        exclude = ['uuid']


# ItemLanguageRelation filter
class ItemLanguageRelationFilter(django_filters.FilterSet):
    item = django_filters.Filter(field_name='item__short_title', lookup_expr='icontains')

    class Meta:
        model = ItemLanguageRelation
        exclude = ['uuid']


# ItemMaterialDetailsRelation filter
class ItemMaterialDetailsRelationFilter(django_filters.FilterSet):
    item = django_filters.Filter(field_name='item__short_title', lookup_expr='icontains')

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
    item = django_filters.Filter(field_name='item__short_title', lookup_expr='icontains')

    class Meta:
        model = ItemWorkRelation
        exclude = ['uuid']


# Language filter
class LanguageFilter(QBasedFilterset):
    collection = ModelMultipleChoiceFilterQ(
        label="Collection",
        queryset=Collection.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Collection,
            search_fields=['short_title__icontains']
        ),
        field_name='items__item__lot__collection',
        lookup_expr='in'
    )
    collection_publication_year = RangeFilterQ(
        label="Collection publication year",
        widget=RangeWidget(),
        field_name='items__item__lot__collection__year_of_publication'
    )
    collection_country_of_publication = ModelMultipleChoiceFilterQ(
        label="Collection country of publication",
        queryset=Country.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Country,
            search_fields=['name__icontains']
        ),
        method='collection_country_of_publication_filter'
    )
    collection_tag = ModelMultipleChoiceFilterQ(
        label="Collection tag",
        queryset=Tag.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Tag,
            search_fields=['namespace__icontains', 'name__icontains', 'value__icontains']
        ),
        method='collection_tag_filter'
    )
    collection_owner_religion = ModelMultipleChoiceFilterQ(
        label="Collection owner religion",
        queryset=Religion.objects.all().order_by('name'),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        method='collection_owner_religion_filter'
    )

    class Meta:
        model = Language
        exclude = ['uuid']

    # Override method
    @property
    def qs(self):
        qs = super().qs
        self._qs = qs.distinct() \
            .annotate(item_count=Count('items__item', filter=Q(items__item__non_book=False), distinct=True)) \
            .order_by('-item_count')
        return self._qs

    def collection_country_of_publication_filter(self, q, name, value):
        if value:
            q &= Q(items__item__lot__collection__related_places__type__name='publication',
                   items__item__lot__collection__related_places__place__country__in=value)
        return q

    def collection_tag_filter(self, q, name, value):
        if value:
            q &= Q(items__item__lot__collection__tags__tag__in=value)
        return q

    def collection_owner_religion_filter(self, q, name, value):
        if value:
            q &= Q(items__item__lot__collection__personcollectionrelation__role__name='owner',
              items__item__lot__collection__personcollectionrelation__person__religiousaffiliation__religion__in=value)
        return q


# MaterialDetails filter
class MaterialDetailsFilter(django_filters.FilterSet):
    class Meta:
        model = MaterialDetails
        exclude = ['uuid']


# PersonItemRelation filter
class PersonItemRelationFilter(django_filters.FilterSet):
    item = django_filters.Filter(field_name='item__short_title', lookup_expr='icontains')

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
    items = django_filters.Filter(field_name='items__short_title', lookup_expr='icontains')
    year = django_filters.RangeFilter(
        label="Year of publication",
        widget=RangeWidget(),
        method='year_filter'
    )
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
    collection = django_filters.ModelMultipleChoiceFilter(
        label="Collection",
        queryset=Collection.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Collection,
            search_fields=['short_title__icontains', 'full_title__icontains',
                           'preface_and_paratexts__icontains']
        ),
        method='collection_filter'
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
        exclude = ['uuid', 'year_start', 'year_end']

    def year_filter(self, queryset, name, value):
        if value:
            if value.start and not value.stop:
                q = Q(year_start__gte=value.start) | Q(year_end__gte=value.start)
            elif value.stop and not value.start:
                q = Q(year_start__lte=value.stop)
            else:  # value.start and value.end
                # Either year_start  within value range
                # or     year_end    within value range
                # or     value range inside range of year_start to year_end
                q = (Q(year_start__gte=value.start) & Q(year_start__lte=value.stop)) \
                    | (Q(year_end__gte=value.start) & Q(year_end__lte=value.stop)) \
                    | (Q(year_start__lte=value.start) & Q(year_end__gte=value.stop))

            return queryset.filter(q)
        return queryset

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

    def collection_filter(self, queryset, name, value):
        if value:
            return queryset.filter(items__lot__collection__in=value)
        return queryset

    def language_filter(self, queryset, name, value):
        if value:
            return queryset.filter(items__languages__language__in=value)
        return queryset

    def book_format_filter(self, queryset, name, value):
        if value:
            return queryset.filter(items__book_format__in=value)
        return queryset


class EditionRankingFilter(EditionFilter):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.request = request
        print("Filter", self.request)

    # Override method
    @property
    def qs(self):
        qs = super().qs
        self._qs = qs.distinct() \
            .annotate(item_count=Count('items', distinct=True)) \
            .annotate(collection_count=Count('items__lot__collection',
                                            filter=Q(items__lot__collection__in=
                                                get_collections_for_session(self.request)),
                                            distinct=True)) \
            .order_by('-item_count')
        return self._qs


# Publisher filter
class PublisherFilter(django_filters.FilterSet):
    publisher = django_filters.Filter(field_name='publisher__short_name', lookup_expr='icontains')
    edition = django_filters.Filter(field_name='edition__item__short_title', lookup_expr='icontains')
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
class WorkFilter(QBasedFilterset):
    title = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    collection_publication_year = RangeFilterQ(label="Collection publication year", widget=RangeWidget(),
                                                        field_name='items__item__lot__collection__year_of_publication',
                                                        lookup_expr='range')
    collection_country = ModelMultipleChoiceFilterQ(
        label="Collection country",
        queryset=Country.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
        field_name='items__item__lot__collection__related_places__place__country',
        lookup_expr='in'
    )
    collection_city = ModelMultipleChoiceFilterQ(
        label="Collection city",
        queryset=Place.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
        field_name='items__item__lot__collection__related_places__place',
        lookup_expr='in'
    )
    collection_owner_gender = MultipleChoiceFilterQWithExtraLookups(
        label="Collection owner gender",
        choices=Person.SEX_CHOICES,
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
        method='collection_owner_gender_filter'
    )
    collection_owner_religion = ModelMultipleChoiceFilterQ(
        label="Collection owner religion",
        queryset=Religion.objects.all().order_by('name'),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        method='collection_owner_religion_filter'
    )
    item_count = django_filters.RangeFilter(
        label="Item count",
        widget=RangeWidget(),
        method='item_count_filter'
    )

    class Meta:
        model = Work
        exclude = ['viaf_id', 'uuid']

    # Override method
    @property
    def qs(self):
        qs = super().qs
        self._qs = qs.distinct()
        return self._qs

    def multiple_words_filter(self, queryset, name, value):
        return filter_multiple_words(self.filters[name].lookup_expr, queryset, name, value)

    def collection_owner_gender_filter(self, q, name, value):
        if value:
            q &= Q(items__item__lot__collection__personcollectionrelation__in=
                                   PersonCollectionRelation.objects.filter(role__name__iexact='owner',
                                                                           person__sex__in=value))
        return q

    def collection_owner_religion_filter(self, q, name, value):
        if value:
            q &= Q(items__item__lot__collection__personcollectionrelation__role__name='owner',
                items__item__lot__collection__personcollectionrelation__person__religiousaffiliation__religion__in=value)
        return q

    def item_count_filter(self, queryset, name, value):
        # value is a slice object
        if value.start or value.stop:
            queryset = queryset.annotate(item_count=Count('items__item', distinct=True))
            if value.start:
                queryset = queryset.filter(item_count__gte=value.start)
            if value.stop:
                queryset = queryset.filter(item_count__lte=value.stop)
        return queryset


# Work Ranking filter
class WorkRankingFilter(WorkFilter):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.request = request

    # Override method
    @property
    def qs(self):
        qs = super().qs
        self._qs = qs.distinct() \
            .annotate(item_count=Count('items__item',
                                       filter=Q(items__item__lot__collection__in=
                                                get_collections_for_session(self.request)),
                                       distinct=True)) \
            .annotate(collection_count=Count('items__item__lot__collection',
                                            filter=Q(items__item__lot__collection__in=
                                                     get_collections_for_session(self.request)),
                                            distinct=True)) \
            .order_by('-item_count')
        return self._qs


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


