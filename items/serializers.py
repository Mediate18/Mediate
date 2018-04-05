from items.models import *
from rest_framework import serializers


class BindingMaterialDetailsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BindingMaterialDetails
        fields = "__all__"


class BookFormatSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BookFormat
        fields = "__all__"


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


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"


class LanguageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Language
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


class PersonItemRelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonItemRelation
        fields = "__all__"


class PersonItemRelationRoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PersonItemRelationRole
        fields = "__all__"


class PublicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Publication
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
