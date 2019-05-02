from .models import *
from rest_framework import serializers


class BookFormatSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BookFormat
        fields = "__all__"


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"


class ItemAuthorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ItemAuthor
        fields = "__all__"


class ItemItemTypeRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ItemItemTypeRelation
        fields = "__all__"


class ItemLanguageRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ItemLanguageRelation
        fields = "__all__"


class ItemMaterialDetailsRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ItemMaterialDetailsRelation
        fields = "__all__"


class ItemTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ItemType
        fields = "__all__"


class ItemWorkRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ItemWorkRelation
        fields = "__all__"


class LanguageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Language
        fields = "__all__"


class MaterialDetailsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MaterialDetails
        fields = "__all__"


class PersonItemRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonItemRelation
        fields = "__all__"


class PersonItemRelationRoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonItemRelationRole
        fields = "__all__"


class EditionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Edition
        fields = "__all__"


class PublisherSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Publisher
        fields = "__all__"


class SubjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class WorkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Work
        fields = "__all__"


class WorkAuthorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkAuthor
        fields = "__all__"


class WorkSubjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkSubject
        fields = "__all__"
