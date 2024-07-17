from rest_framework import viewsets
from ..serializers import *


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    http_method_names = ['get']


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    http_method_names = ['get']


class ReligionViewSet(viewsets.ModelViewSet):
    queryset = Religion.objects.all()
    serializer_class = ReligionSerializer
    http_method_names = ['get']


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    http_method_names = ['get']


class ReligiousAffiliationViewSet(viewsets.ModelViewSet):
    queryset = ReligiousAffiliation.objects.all()
    serializer_class = ReligiousAffiliationSerializer
    http_method_names = ['get']


class ResidenceViewSet(viewsets.ModelViewSet):
    queryset = Residence.objects.all()
    serializer_class = ResidenceSerializer
    http_method_names = ['get']


class ProfessionViewSet(viewsets.ModelViewSet):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer
    http_method_names = ['get']


class PersonProfessionViewSet(viewsets.ModelViewSet):
    queryset = PersonProfession.objects.all()
    serializer_class = PersonProfessionSerializer
    http_method_names = ['get']


class PersonPersonRelationTypeViewSet(viewsets.ModelViewSet):
    queryset = PersonPersonRelationType.objects.all()
    serializer_class = PersonPersonRelationTypeSerializer
    http_method_names = ['get']


class PersonPersonRelationViewSet(viewsets.ModelViewSet):
    queryset = PersonPersonRelation.objects.all()
    serializer_class = PersonPersonRelationSerializer
    http_method_names = ['get']

