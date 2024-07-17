from .models import *
from rest_framework import serializers


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dataset
        fields = "__all__"


class CollectionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Collection
        fields = "__all__"


class CollectionTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CollectionType
        fields = "__all__"


class CatalogueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Catalogue
        fields = "__all__"


class LotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Lot
        fields = "__all__"


class PersonCollectionRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonCollectionRelation
        fields = "__all__"


class PersonCollectionRelationRoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonCollectionRelationRole
        fields = "__all__"


class PersonCatalogueRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonCatalogueRelation
        fields = "__all__"


class CatalogueYearSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CatalogueYear
        fields = "__all__"


class LibrarySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Library
        fields = "__all__"


class CollectionCollectionTypeRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CollectionCollectionTypeRelation
        fields = "__all__"


class CollectionHeldBySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CollectionHeldBy
        fields = "__all__"


class ParisianCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ParisianCategory
        fields = "__all__"


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
