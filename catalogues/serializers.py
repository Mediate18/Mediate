from .models import *
from rest_framework import serializers


class CatalogueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Collection
        fields = "__all__"


class CatalogueTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CollectionType
        fields = "__all__"


class Collection_TMPSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Collection_TMP
        fields = "__all__"


class LotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Lot
        fields = "__all__"


class PersonCatalogueRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonCollectionRelation
        fields = "__all__"


class PersonCatalogueRelationRoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonCollectionRelationRole
        fields = "__all__"


class PersonCollection_TMPRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonCollection_TMPRelation
        fields = "__all__"


class Collection_TMPYearSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Collection_TMPYear
        fields = "__all__"


class LibrarySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Library
        fields = "__all__"


class CatalogueCatalogueTypeRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CollectionCollectionTypeRelation
        fields = "__all__"


class CatalogueHeldBySerializer(serializers.HyperlinkedModelSerializer):
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
