import django_filters
from .models import *
from viapy.api import ViafAPI
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django_select2.forms import Select2MultipleWidget

from mediate.tools import filter_multiple_words
from catalogues.models import PersonCatalogueRelationRole, Catalogue
from items.models import PersonItemRelationRole, Edition


# Person filter
class PersonFilter(django_filters.FilterSet):
    short_name = django_filters.Filter(lookup_expr='icontains')
    surname = django_filters.Filter(lookup_expr='icontains')
    sex = django_filters.MultipleChoiceFilter(
        choices=Person.SEX_CHOICES,
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    city_of_birth = django_filters.ModelMultipleChoiceFilter(
        queryset=Place.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},)
    )
    city_of_death = django_filters.ModelMultipleChoiceFilter(
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
        field_name='religious_affiliation__religion',
        lookup_expr='in'
    )
    city_of_residence = django_filters.ModelMultipleChoiceFilter(
        label="City of residence",
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
    published_catalogues = django_filters.ModelMultipleChoiceFilter(
        label="Catalogues",
        queryset=Catalogue.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
        method='published_catalogues_filter'
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

    def published_catalogues_filter(self, queryset, name, value):
        if value:
            return queryset.filter(published_catalogues__catalogue__in=value)
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


