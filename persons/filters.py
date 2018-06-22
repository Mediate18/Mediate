import django_filters
from .models import *
from viapy.api import ViafAPI
from django.utils.translation import ugettext_lazy as _


# Person filter
class PersonFilter(django_filters.FilterSet):
    from django_select2.forms import Select2MultipleWidget
    short_name = django_filters.Filter(lookup_expr='icontains')
    first_names = django_filters.Filter(lookup_expr='icontains')
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
    viaf_id = django_filters.Filter(method='viaf_id_filter')

    class Meta:
        model = Person
        exclude = ['uuid']
        fields = [
            'short_name',
            'first_names',
            'surname',
            'sex',
            'city_of_birth',
            'date_of_birth',
            'city_of_death',
            'date_of_death',
            'viaf_id'
        ]

    def viaf_id_filter(self, queryset, name, value):
        if value:
            return queryset.filter(viaf_id=ViafAPI.uri_base+"/"+value)
        return queryset


# PersonPersonRelation filter
class PersonPersonRelationFilter(django_filters.FilterSet):
    class Meta:
        model = PersonPersonRelation
        fields = "__all__"


# PersonPersonRelationType filter
class PersonPersonRelationTypeFilter(django_filters.FilterSet):
    class Meta:
        model = PersonPersonRelationType
        fields = "__all__"


# PersonProfession filter
class PersonProfessionFilter(django_filters.FilterSet):
    class Meta:
        model = PersonProfession
        fields = "__all__"


# Place filter
class PlaceFilter(django_filters.FilterSet):
    class Meta:
        model = Place
        fields = "__all__"


# Profession filter
class ProfessionFilter(django_filters.FilterSet):
    class Meta:
        model = Profession
        fields = "__all__"


# Religion filter
class ReligionFilter(django_filters.FilterSet):
    class Meta:
        model = Religion
        fields = "__all__"


# ReligiousAffiliation filter
class ReligiousAffiliationFilter(django_filters.FilterSet):
    class Meta:
        model = ReligiousAffiliation
        fields = "__all__"


# Residence filter
class ResidenceFilter(django_filters.FilterSet):
    class Meta:
        model = Residence
        fields = "__all__"


