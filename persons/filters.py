import django_filters
from .models import *
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, IntegerField, Count
from django.db.models.functions import Cast
from django_select2.forms import Select2MultipleWidget, ModelSelect2MultipleWidget
from django_filters.widgets import RangeWidget
from django.utils.safestring import mark_safe

from apiconnectors.viafapi import ViafAPI
from mediate.tools import filter_multiple_words
from mediate.filters import QBasedFilter, RangeFilterQ, RangeRangeFilterQ, MultipleChoiceFilterQWithExtraLookups, \
    ModelMultipleChoiceFilterQ, ModelMultipleChoiceFilterQWithExtraLookups, QBasedFilterset
from catalogues.models import PersonCollectionRelationRole, Collection
from catalogues.views.views import get_collections_for_session
from items.models import PersonItemRelationRole
from tagme.models import Tag


# Person filter
class PersonFilter(django_filters.FilterSet):
    city_of_birth_text = 'city of birth'
    city_of_death_text = 'city of death'
    city_of_residence_text = 'city of residence'
    place_help = ' <span class="glyphicon glyphicon-question-sign" ' \
                 'title="When known, the MEDIATE database lists the {} of Persons. ' \
                 'In other cases, it lists a region, county, or other geographic entity."></span>'

    short_name = django_filters.Filter(method='short_name_filter')
    surname = django_filters.Filter(method='surname_filter')
    sex = django_filters.MultipleChoiceFilter(
        choices=Person.SEX_CHOICES,
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    city_of_birth = django_filters.ModelMultipleChoiceFilter(
        label=mark_safe(_("Place of birth") + place_help.format(city_of_birth_text)),
        queryset=Place.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    country_of_birth = django_filters.ModelMultipleChoiceFilter(
        label="Country of birth",
        queryset=Country.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
        field_name='city_of_birth__country',
        lookup_expr='in'
    )
    city_of_death = django_filters.ModelMultipleChoiceFilter(
        label=mark_safe(_("Place of death") + place_help.format(city_of_death_text)),
        queryset=Place.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    country_of_death = django_filters.ModelMultipleChoiceFilter(
        label="Country of death",
        queryset=Country.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
        field_name='city_of_death__country',
        lookup_expr='in'
    )
    profession = django_filters.ModelMultipleChoiceFilter(
        label="Profession",
        queryset=Profession.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        field_name='personprofession__profession',
        lookup_expr='in'
    )
    collection_roles = django_filters.ModelMultipleChoiceFilter(
        label="Collection roles",
        queryset=PersonCollectionRelationRole.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        field_name='personcollectionrelation__role',
        lookup_expr='in'
    )
    item_roles = django_filters.ModelMultipleChoiceFilter(
        label="Item roles",
        queryset=PersonItemRelationRole.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        field_name='personitemrelation__role',
        lookup_expr='in'
    )
    work_author = django_filters.BooleanFilter(label="Work author", field_name='works', lookup_expr='isnull',
                                               exclude=True)
    publisher = django_filters.BooleanFilter(label="Publisher", field_name='publisher', lookup_expr='isnull',
                                             exclude=True)
    religious_affiliation = django_filters.ModelMultipleChoiceFilter(
        label="Religious affiliation",
        queryset=Religion.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        field_name='religiousaffiliation__religion',
        lookup_expr='in'
    )
    city_of_residence = django_filters.ModelMultipleChoiceFilter(
        label=mark_safe(_("Place of residence") + place_help.format(city_of_residence_text)),
        queryset=Place.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        field_name='residence__place',
        lookup_expr='in'
    )
    country_of_residence = django_filters.ModelMultipleChoiceFilter(
        label="Country of residence",
        queryset=Country.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
        field_name='residence__place__country',
        lookup_expr='in'
    )
    related_to = django_filters.ModelMultipleChoiceFilter(
        label="Related to",
        queryset=Person.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        method='related_to_filter'
    )
    nature_of_relation = django_filters.ModelMultipleChoiceFilter(
        label="Person relation types",
        queryset=PersonPersonRelationType.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        method='nature_of_relation_filter'
    )
    notes = django_filters.Filter(field_name='notes', label='Notes', lookup_expr='icontains')

    class Meta:
        model = Person
        fields = [
            'short_name',
            'surname',
            'sex',
            'city_of_birth',
            'country_of_birth',
            'date_of_birth',
            'city_of_death',
            'country_of_death',
            'date_of_death',
            'profession',
            'collection_roles',
            'item_roles',
            'work_author',
            'publisher',
            'religious_affiliation',
            'city_of_residence',
            'country_of_residence',
            'related_to',
            'nature_of_relation',
            'notes'
        ]

    def short_name_filter(self, queryset, name, value):
        from django.db.models import Q
        if value:
            short_name_q = Q(short_name__icontains=value)
            alternative_short_name_q = Q(alternative_names__short_name__icontains=value)
            return queryset.filter(short_name_q | alternative_short_name_q)
        return queryset

    def surname_filter(self, queryset, name, value):
        from django.db.models import Q
        if value:
            surname_q = Q(surname__icontains=value)
            alternative_surname_q = Q(alternative_names__surname__icontains=value)
            return queryset.filter(surname_q | alternative_surname_q)
        return queryset

    def viaf_id_filter(self, queryset, name, value):
        if value:
            return queryset.filter(viaf_id=ViafAPI.uri_base+"/"+value)
        return queryset

    def related_to_filter(self, queryset, name, value):
        if value:
            first_person_query = Q(relations_when_first__second_person__in=value)
            second_person_query = Q(relations_when_second__first_person__in=value)
            return queryset.filter(first_person_query | second_person_query).distinct()
        return queryset

    def nature_of_relation_filter(self, queryset, name, value):
        if value:
            first_person_query = Q(relations_when_first__type__in=value)
            second_person_query = Q(relations_when_second__type__in=value)
            return queryset.filter(first_person_query | second_person_query).distinct()
        return queryset


class PersonRankingFilter(QBasedFilterset):
    item_roles = ModelMultipleChoiceFilterQ(
        label="Item roles",
        queryset=PersonItemRelationRole.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        field_name='personitemrelation__role',
        lookup_expr='in',
        required=True
    )
    edition_year = RangeRangeFilterQ(
        label="Item publication year",
        widget=RangeWidget(),
        field_names=('personitemrelation__item__edition__year_start', 'personitemrelation__item__edition__year_end'),
        lookup_expr='range',
    )
    collection_publication_country = ModelMultipleChoiceFilterQ(
        label="Collection country",
        queryset=Country.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        field_name='personitemrelation__item__lot__collection__related_places__place__country',
        lookup_expr='in',
    )
    sex = MultipleChoiceFilterQWithExtraLookups(
        label="Gender of Person related to Item",
        choices=Person.SEX_CHOICES,
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        lookup_expr='in',
    )
    collection_year = RangeFilterQ(
        label="Collection publication year",
        widget=RangeWidget(),
        field_name='personitemrelation__item__lot__collection__year_of_publication',
        lookup_expr='range'
    )
    collection_owner_sex = MultipleChoiceFilterQWithExtraLookups(
        label="Collection owner gender",
        choices=Person.SEX_CHOICES,
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        field_name='personitemrelation__item__lot__collection__personcollectionrelation__person__sex',
        lookup_expr='in',
        extra_field_lookups={'personitemrelation__item__lot__collection__personcollectionrelation__role__name': 'owner'}
    )
    collection_owner_religion = ModelMultipleChoiceFilterQWithExtraLookups(
        label="Collection owner religion",
        queryset=Religion.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        field_name=
        'personitemrelation__item__lot__collection__personcollectionrelation__person__religiousaffiliation__religion',
        lookup_expr='in',
        extra_field_lookups={'personitemrelation__item__lot__collection__personcollectionrelation__role__name': 'owner'}
    )
    country_of_birth = ModelMultipleChoiceFilterQ(
        label="Country of birth of Person related to Item",
        queryset=Country.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        field_name='city_of_birth__country',
        lookup_expr='in'
    )
    country_of_death = ModelMultipleChoiceFilterQ(
        label="Country of death of Person related to Item",
        queryset=Country.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        field_name='city_of_death__country',
        lookup_expr='in'
    )
    date_of_birth = django_filters.Filter(
        widget=RangeWidget(),
        method='year_text_range_filter'
    )
    date_of_death = django_filters.Filter(
        widget=RangeWidget(),
        method='year_text_range_filter'
    )

    class Meta:
        model = Person
        fields = [
            'item_roles',
            'edition_year',
            'collection_publication_country',
            'sex',
            'collection_year',
            'collection_owner_sex',
            'collection_owner_religion',
            'country_of_birth',
            'date_of_birth',
            'country_of_death',
            'date_of_death'
        ]

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.request = request
        self.fields_with_errors = []

    # Override method
    @property
    def qs(self):
        if hasattr(self, '_qs') and self._qs:
            return self._qs

        qs = super().qs
        self._qs = qs.distinct() \
            .annotate(item_count=Count('personitemrelation__item',
                                       filter=Q(personitemrelation__item__lot__collection__in=
                                         get_collections_for_session(self.request)),
                                       distinct=True)) \
            .annotate(collection_count=Count('personitemrelation__item__lot__collection',
                                       filter=Q(personitemrelation__item__lot__collection__in=
                                         get_collections_for_session(self.request)),
                                        distinct=True)) \
            .order_by('-item_count')
        return self._qs

    def year_text_range_filter(self, queryset, name, value):
        """
        Filters on text fields containing year data using a range value.
        The name of the filter should reflect the field name in the model.
        :param queryset: the queryset to alter
        :param name: the name of the filter
        :param value: the value from the form
        :return: 
        """
        if not (isinstance(value, list) and any(value)):
            return queryset

        try:
            year_range = [int(year) if year else None for year in value]
        except ValueError as ve:
            self.form.add_error(name, "Invalid input. Use only integers.")
            self.fields_with_errors.append(name)
            return queryset

        if year_range[0] and year_range[1]:
            int_filter = {name+'_int__range': (year_range[0], year_range[1])}
        elif value[0]:
            int_filter = {name+'_int__gte': year_range[0]}
        elif value[1]:
            int_filter = {name+'_int__lte': year_range[1]}
        return queryset.filter(**{name + '__regex': r'^[0-9]{3,4}$'}) \
            .annotate(**{name + '_int': Cast(name, IntegerField())}) \
            .filter(**int_filter)


# PersonPersonRelation filter
class PersonPersonRelationFilter(django_filters.FilterSet):
    class Meta:
        model = PersonPersonRelation
        exclude = ['uuid']


# PersonPersonRelationType filter
class PersonPersonRelationTypeFilter(django_filters.FilterSet):
    class Meta:
        model = PersonPersonRelationType
        exclude = ['uuid']


# PersonProfession filter
class PersonProfessionFilter(django_filters.FilterSet):
    class Meta:
        model = PersonProfession
        exclude = ['uuid']


# Country filter
class CountryFilter(django_filters.FilterSet):
    name = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')

    class Meta:
        model = Country
        exclude = ['uuid']

    def multiple_words_filter(self, queryset, name, value):
        return filter_multiple_words(self.filters[name].lookup_expr, queryset, name, value)


# Country filter
class CountryRankingFilter(CountryFilter):
    # Override method
    @property
    def qs(self):
        qs = super().qs
        self._qs = qs.distinct() \
            .annotate(item_count=Count('place__edition__items',
                                       filter=Q(place__edition__items__lot__collection__in=
                                         get_collections_for_session(self.request)),
                                       distinct=True)) \
            .annotate(collection_count=Count('place__edition__items__lot__collection',
                                       filter=Q(place__edition__items__lot__collection__in=
                                         get_collections_for_session(self.request)),
                                       distinct=True)) \
            .order_by('-item_count')
        return self._qs


# Place filter
class PlaceFilter(django_filters.FilterSet):
    name = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    country = django_filters.ModelMultipleChoiceFilter(
        queryset=Country.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )

    class Meta:
        model = Place
        exclude = ['uuid']

    def multiple_words_filter(self, queryset, name, value):
        return filter_multiple_words(self.filters[name].lookup_expr, queryset, name, value)


class PlaceRankingFilter(QBasedFilterset, PlaceFilter):
    year = RangeFilterQ(
        label="Item publication year",
        widget=RangeWidget(),
        field_name='edition__year_start'
    )
    collection = ModelMultipleChoiceFilterQ(
        label="Collection",
        queryset=Collection.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={'data-placeholder': "Select multiple"},
            model=Collection,
            search_fields=['short_title__icontains']
        ),
        field_name='edition__items__lot__collection',
        lookup_expr='in'
    )
    collection_short_title = django_filters.Filter(
        label="Collection short title",
        lookup_expr='icontains',
        method='collection_short_title_multiple_words_filter',
        field_name='edition__items__lot__collection__short_title'
    )
    collection_publication_year = RangeFilterQ(
        label="Collection publication year",
        widget=RangeWidget(),
        field_name='edition__items__lot__collection__year_of_publication'
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
        model = Place
        fields = [
            'name', 'cerl_id', 'country'
        ]

    # Override method
    @property
    def qs(self):
        qs = super().qs
        self._qs = qs.distinct() \
            .annotate(item_count=Count('edition__items',
                                       filter=Q(edition__items__lot__collection__in=
                                         get_collections_for_session(self.request)),
                                       distinct=True)) \
            .annotate(collection_count=Count('edition__items__lot__collection',
                                       filter=Q(edition__items__lot__collection__in=
                                         get_collections_for_session(self.request)),
                                       distinct=True)) \
            .order_by('-item_count')
        return self._qs

    def collection_short_title_multiple_words_filter(self, queryset, name, value):
        return filter_multiple_words(self.filters['collection_short_title'].lookup_expr, queryset, name, value)

    def collection_country_of_publication_filter(self, q, name, value):
        if value:
            q &= Q(edition__items__lot__collection__related_places__type__name='publication',
                   edition__items__lot__collection__related_places__place__country__in=value)
        return q

    def collection_tag_filter(self, q, name, value):
        if value:
            q &= Q(edition__items__lot__collection__tags__tag__in=value)
        return q

    def collection_owner_religion_filter(self, q, name, value):
        if value:
            q &= Q(edition__items__lot__collection__personcollectionrelation__role__name='owner',
              edition__items__lot__collection__personcollectionrelation__person__religiousaffiliation__religion__in=value)
        return q

    def get_year_range(self):
        if self.data:
            year_0 = int(self.data['year_0']) if 'year_0' in self.data and self.data['year_0'] else None
            year_1 = int(self.data['year_1']) if 'year_1' in self.data and self.data['year_1'] else None
            return (year_0, year_1)
        else:
            return None

    def get_collections(self):
        if self.data:
            return self.data.getlist('collection')
        else:
            return None


# PlaceLinks filter
class PlaceLinksFilter(django_filters.FilterSet):
    name = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    country = django_filters.ModelMultipleChoiceFilter(
        queryset=Country.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    related_collections = django_filters.ModelMultipleChoiceFilter(
        label="Collections",
        queryset=Collection.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
        method='related_collections_filter'
    )
    persons = django_filters.ModelMultipleChoiceFilter(
        label="People born/inhabiting/died",
        queryset=Person.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        method='persons_filter'
    )

    class Meta:
        model = Place
        exclude = ['uuid', 'cerl_id']

    def multiple_words_filter(self, queryset, name, value):
        return filter_multiple_words(self.filters[name].lookup_expr, queryset, name, value)

    def related_collections_filter(self, queryset, name, value):
        if value:
            return queryset.filter(related_collections__collection__in=value)
        return queryset

    def persons_filter(self, queryset, name, value):
        if value:
            people_born = Q(persons_born__in=value)
            people_died = Q(persons_died__in=value)
            inhabited = Q(residence__person__in=value)
            return queryset.filter(people_born | people_died | inhabited).distinct()
        return queryset


# Profession filter
class ProfessionFilter(django_filters.FilterSet):
    class Meta:
        model = Profession
        exclude = ['uuid']


# Religion filter
class ReligionFilter(django_filters.FilterSet):
    class Meta:
        model = Religion
        exclude = ['uuid']


# ReligiousAffiliation filter
class ReligiousAffiliationFilter(django_filters.FilterSet):
    class Meta:
        model = ReligiousAffiliation
        exclude = ['uuid']


# Residence filter
class ResidenceFilter(django_filters.FilterSet):
    class Meta:
        model = Residence
        exclude = ['uuid']


