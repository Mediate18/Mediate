from rest_framework import viewsets
from ..serializers import *


class BookFormatViewSet(viewsets.ModelViewSet):
    queryset = BookFormat.objects.all()
    serializer_class = BookFormatSerializer
    http_method_names = ['get']


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    http_method_names = ['get']


class ItemAuthorViewSet(viewsets.ModelViewSet):
    queryset = ItemAuthor.objects.all()
    serializer_class = ItemAuthorSerializer
    http_method_names = ['get']


class ItemItemTypeRelationViewSet(viewsets.ModelViewSet):
    queryset = ItemItemTypeRelation.objects.all()
    serializer_class = ItemItemTypeRelationSerializer
    http_method_names = ['get']


class ItemLanguageRelationViewSet(viewsets.ModelViewSet):
    queryset = ItemLanguageRelation.objects.all()
    serializer_class = ItemLanguageRelationSerializer
    http_method_names = ['get']


class ItemMaterialDetailsRelationViewSet(viewsets.ModelViewSet):
    queryset = ItemMaterialDetailsRelation.objects.all()
    serializer_class = ItemMaterialDetailsRelationSerializer
    http_method_names = ['get']


class ItemTypeViewSet(viewsets.ModelViewSet):
    queryset = ItemType.objects.all()
    serializer_class = ItemTypeSerializer
    http_method_names = ['get']


class ItemWorkRelationViewSet(viewsets.ModelViewSet):
    queryset = ItemWorkRelation.objects.all()
    serializer_class = ItemWorkRelationSerializer
    http_method_names = ['get']


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    http_method_names = ['get']


class MaterialDetailsViewSet(viewsets.ModelViewSet):
    queryset = MaterialDetails.objects.all()
    serializer_class = MaterialDetailsSerializer
    http_method_names = ['get']


class PersonItemRelationViewSet(viewsets.ModelViewSet):
    queryset = PersonItemRelation.objects.all()
    serializer_class = PersonItemRelationSerializer
    http_method_names = ['get']


class PersonItemRelationRoleViewSet(viewsets.ModelViewSet):
    queryset = PersonItemRelationRole.objects.all()
    serializer_class = PersonItemRelationRoleSerializer
    http_method_names = ['get']


class EditionViewSet(viewsets.ModelViewSet):
    queryset = Edition.objects.all()
    serializer_class = EditionSerializer
    http_method_names = ['get']


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    http_method_names = ['get']


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    http_method_names = ['get']


class WorkViewSet(viewsets.ModelViewSet):
    queryset = Work.objects.all()
    serializer_class = WorkSerializer
    http_method_names = ['get']


class WorkAuthorViewSet(viewsets.ModelViewSet):
    queryset = WorkAuthor.objects.all()
    serializer_class = WorkAuthorSerializer
    http_method_names = ['get']


class WorkSubjectViewSet(viewsets.ModelViewSet):
    queryset = WorkSubject.objects.all()
    serializer_class = WorkSubjectSerializer
    http_method_names = ['get']
