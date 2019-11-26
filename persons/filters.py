import django_filters
from .models import *
from viapy.api import ViafAPI
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q, IntegerField, Count
from django.db.models.functions import Cast
from django import forms
from django_select2.forms import Select2MultipleWidget
from django_filters.widgets import RangeWidget
from django.utils.safestring import mark_safe

import six
from django_filters.constants import STRICTNESS
from django_filters.filters import Lookup

from mediate.tools import filter_multiple_words
from catalogues.models import PersonCatalogueRelationRole, Catalogue
from items.models import PersonItemRelationRole


# Person filter
class PersonFilter(django_filters.FilterSet):
    city_of_birth_text = 'city of birth'
    city_of_death_text = 'city of death'
    city_of_residence_text = 'city of residence'
    place_help = ' <span class="glyphicon glyphicon-question-sign" ' \
                 'title="When known, the MEDIATE database lists the {} of Persons. ' \
                 'In other cases, it lists a region, county, or other geographic entity."></span>'

    short_name = django_filters.Filter(method='short_name_filter')
    first_names = django_filters.Filter(method='first_names_filter')
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
    city_of_death = django_filters.ModelMultipleChoiceFilter(
        label=mark_safe(_("Place of death") + place_help.format(city_of_death_text)),
        queryset=Place.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    profession = django_filters.ModelMultipleChoiceFilter(
        label="Profession",
        queryset=Profession.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        field_name='personprofession__profession',
        lookup_expr='in'
    )
    catalogue_roles = django_filters.ModelMultipleChoiceFilter(
        label="Catalogue roles",
        queryset=PersonCatalogueRelationRole.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        field_name='personcataloguerelation__role',
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

    class Meta:
        model = Person
        fields = [
            'short_name',
            'first_names',
            'surname',
            'sex',
            'city_of_birth',
            'date_of_birth',
            'city_of_death',
            'date_of_death',
            'profession',
            'catalogue_roles',
            'item_roles',
            'work_author',
            'publisher',
            'religious_affiliation',
            'city_of_residence',
            'related_to',
            'nature_of_relation'
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

    def first_names_filter(self, queryset, name, value):
        from django.db.models import Q
        if value:
            first_names_q = Q(first_names=value)
            alternative_first_names_q = Q(alternative_names__first_names__icontains=value)
            return queryset.filter(first_names_q | alternative_first_names_q)
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


class QBasedFilter:
    """
    Merely a super class for testing with isinstance.
    """
    pass


class ModelMultipleChoiceFilterQ(QBasedFilter, django_filters.ModelMultipleChoiceFilter):
    """
    Subclass of django_filters.ModelMultipleChoiceFilter for the purpose of
    using Q objects within one filter instead of chaining filters.
    """

    def filter(self, q, value):
        """ModelMultipleChoiceFilter filter method override for use of Q(...) """
        if isinstance(value, Lookup):
            lookup = six.text_type(value.lookup_type)
            value = value.value
        else:
            lookup = self.lookup_expr
        if not value:
            return q
        q &= Q(**{'%s__%s' % (self.field_name, lookup): value})
        return q


class RangeFilterQ(QBasedFilter, django_filters.RangeFilter):
    """
    Subclass of django_filters.RangeFilter for the purpose of
    using Q objects within one filter instead of chaining filters.
    """

    def filter(self, q, value):
        """RangeFilter filter method override for use of Q(...) """
        if value:
            if value.start is not None and value.stop is not None:
                lookup = '%s__range' % self.field_name
                return q & Q(**{lookup: (value.start, value.stop)})
            else:
                if value.start is not None:
                    q &= Q(**{'%s__gte' % self.field_name: value.start})
                if value.stop is not None:
                    q &= Q(**{'%s__lte' % self.field_name: value.stop})
        return q


class MultipleChoiceFilterQWithExtraLookups(QBasedFilter, django_filters.MultipleChoiceFilter):
    """
    Subclass of django_filters.MultipleChoiceFilter for the purpose of
    using Q objects within one filter instead of chaining filters.
    Specific version for the catalogue_owner_sex in PersonRankingFilter.
    """

    def __init__(self, *args, **kwargs):
        self.extra_field_lookups = kwargs.pop('extra_field_lookups', {})
        super().__init__(*args, **kwargs)

    def filter(self, q, value):
        """MultipleChoiceFilter filter method override for use of Q(...) """
        if isinstance(value, Lookup):
            lookup = six.text_type(value.lookup_type)
            value = value.value
        else:
            lookup = self.lookup_expr
        if not value:
            return q
        q &= Q(**{'%s__%s' % (self.field_name, lookup): value, **self.extra_field_lookups})
        return q


class PersonRankingFilter(django_filters.FilterSet):
    item_roles = ModelMultipleChoiceFilterQ(
        label="Item roles",
        queryset=PersonItemRelationRole.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        field_name='personitemrelation__role',
        lookup_expr='in',
        required=True
    )
    edition_year = RangeFilterQ(
        label="Item publication year",
        widget=RangeWidget(),
        field_name='personitemrelation__item__edition__year',
        lookup_expr='range',
    )
    catalogue_publication_country = ModelMultipleChoiceFilterQ(
        label="Catalogue country",
        queryset=Country.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        field_name='personitemrelation__item__lot__catalogue__related_places__place__country',
        lookup_expr='in',
    )
    sex = MultipleChoiceFilterQWithExtraLookups(
        label="Gender of Person related to Item",
        choices=Person.SEX_CHOICES,
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        lookup_expr='in',
    )
    catalogue_year = RangeFilterQ(
        label="Catalogue publication year",
        widget=RangeWidget(),
        field_name='personitemrelation__item__lot__catalogue__year_of_publication',
        lookup_expr='range'
    )
    catalogue_owner_sex = MultipleChoiceFilterQWithExtraLookups(
        label="Catalogue owner gender",
        choices=Person.SEX_CHOICES,
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"}, ),
        field_name='personitemrelation__item__lot__catalogue__personcataloguerelation__person__sex',
        lookup_expr='in',
        extra_field_lookups={'personitemrelation__item__lot__catalogue__personcataloguerelation__role__name': 'owner'}
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
            'catalogue_publication_country',
            'sex',
            'catalogue_year',
            'catalogue_owner_sex',
            'country_of_birth',
            'date_of_birth',
            'country_of_death',
            'date_of_death'
        ]

    # Override method
    @property
    def qs(self):
        if not hasattr(self, '_qs'):
            if not self.is_bound:
                self._qs = self.queryset.all()
                return self._qs

            if not self.form.is_valid():
                if self.strict == STRICTNESS.RAISE_VALIDATION_ERROR:
                    raise forms.ValidationError(self.form.errors)
                elif self.strict == STRICTNESS.RETURN_NO_RESULTS:
                    self._qs = self.queryset.none()
                    return self._qs
                # else STRICTNESS.IGNORE...  ignoring

            # start with all the results and filter from there
            qs = self.queryset.all()
            query = Q()
            for name, filter_ in six.iteritems(self.filters):
                if isinstance(filter_, QBasedFilter):
                    value = self.form.cleaned_data.get(name)

                    if value is not None:  # valid & clean data
                        query = filter_.filter(query, value)

            qs = qs.filter(query)

            for name, filter_ in six.iteritems(self.filters):
                if not isinstance(filter_, QBasedFilter):
                    value = self.form.cleaned_data.get(name)

                    if value is not None:  # valid & clean data
                        qs = filter_.filter(qs, value)

            self._qs = qs.distinct()\
                .annotate(item_count=Count('uuid'))\
                .annotate(catalogue_count=Count('personitemrelation__item__lot__catalogue', distinct=True))\
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
        if value:
            if value[0] and value[1]:
                queryset = queryset.filter(**{name+'__regex': r'^[0-9]{3,4}$'}) \
                    .annotate(**{name+'_int': Cast(name, IntegerField())})\
                    .filter(**{name+'_int__range': (value[0], value[1])})
            else:
                if value[0]:
                    queryset = queryset.filter(**{name+'__regex': r'^[0-9]{3,4}$'}) \
                        .annotate(**{name+'_int': Cast(name, IntegerField())})\
                        .filter(**{name+'_int__gte': value[0]})
                if value[1]:
                    queryset = queryset.filter(**{name+'__regex': r'^[0-9]{3,4}$'}) \
                        .annotate(**{name+'_int': Cast(name, IntegerField())})\
                        .filter(**{name+'_int__lte': value[1]})

        return queryset


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


# PlaceLinks filter
class PlaceLinksFilter(django_filters.FilterSet):
    name = django_filters.Filter(lookup_expr='icontains', method='multiple_words_filter')
    country = django_filters.ModelMultipleChoiceFilter(
        queryset=Country.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    related_catalogues = django_filters.ModelMultipleChoiceFilter(
        label="Catalogues",
        queryset=Catalogue.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
        method='related_catalogues_filter'
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

    def related_catalogues_filter(self, queryset, name, value):
        if value:
            return queryset.filter(related_catalogues__catalogue__in=value)
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


