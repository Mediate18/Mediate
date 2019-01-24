from .models import *
from rest_framework import serializers


class PlaceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Place
        fields = "__all__"


class ReligionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Religion
        fields = "__all__"


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        fields = "__all__"


class ReligiousAffiliationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ReligiousAffiliation
        fields = "__all__"


class ResidenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Residence
        fields = "__all__"


class ProfessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profession
        fields = "__all__"


class PersonProfessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonProfession
        fields = "__all__"


class PersonPersonRelationTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonPersonRelationType
        fields = "__all__"


class PersonPersonRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonPersonRelation
        fields = "__all__"
