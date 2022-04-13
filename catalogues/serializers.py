from .models import *
from rest_framework import serializers


class CollectionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Collection
        fields = "__all__"


class CollectionTypeSerializer(serializers.HyperlinkedModelSerializer):
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


class PersonCollectionRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonCollectionRelation
        fields = "__all__"


class PersonCollectionRelationRoleSerializer(serializers.HyperlinkedModelSerializer):
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
