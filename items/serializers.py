from items.models import *
from rest_framework import serializers


class CatalogueTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CatalogueType
        fields = "__all__"


class CatalogueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Catalogue
        fields = "__all__"


class CatalogueItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CatalogueItem
        fields = "__all__"


class BookItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BookItem
        fields = "__all__"