import django_filters
from .models import *


# Person filter
class PersonFilter(django_filters.FilterSet):
    class Meta:
        model = Person
        fields = "__all__"


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


