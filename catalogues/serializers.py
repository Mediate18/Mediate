from .models import *
from rest_framework import serializers


class CatalogueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Catalogue
        fields = "__all__"


class CatalogueTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CatalogueType
        fields = "__all__"


class CollectionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Collection
        fields = "__all__"


class LotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Lot
        fields = "__all__"


class PersonCatalogueRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonCatalogueRelation
        fields = "__all__"


class PersonCatalogueRelationRoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonCatalogueRelationRole
        fields = "__all__"


class PersonCollectionRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonCollectionRelation
        fields = "__all__"


class CollectionYearSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CollectionYear
        fields = "__all__"


class LibrarySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Library
        fields = "__all__"


class CatalogueCatalogueTypeRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CatalogueCatalogueTypeRelation
        fields = "__all__"


class CatalogueHeldBySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CatalogueHeldBy
        fields = "__all__"


class ParisianCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ParisianCategory
        fields = "__all__"


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
