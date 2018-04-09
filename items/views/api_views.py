from rest_framework import viewsets
from ..serializers import *


class BookFormatViewSet(viewsets.ModelViewSet):
    queryset = BookFormat.objects.all()
    serializer_class = BookFormatSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class ItemAuthorViewSet(viewsets.ModelViewSet):
    queryset = ItemAuthor.objects.all()
    serializer_class = ItemAuthorSerializer


class ItemBookFormatRelationViewSet(viewsets.ModelViewSet):
    queryset = ItemBookFormatRelation.objects.all()
    serializer_class = ItemBookFormatRelationSerializer


class ItemItemTypeRelationViewSet(viewsets.ModelViewSet):
    queryset = ItemItemTypeRelation.objects.all()
    serializer_class = ItemItemTypeRelationSerializer


class ItemLanguageRelationViewSet(viewsets.ModelViewSet):
    queryset = ItemLanguageRelation.objects.all()
    serializer_class = ItemLanguageRelationSerializer


class ItemMaterialDetailsRelationViewSet(viewsets.ModelViewSet):
    queryset = ItemMaterialDetailsRelation.objects.all()
    serializer_class = ItemMaterialDetailsRelationSerializer


class ItemTypeViewSet(viewsets.ModelViewSet):
    queryset = ItemType.objects.all()
    serializer_class = ItemTypeSerializer


class ItemWorkRelationViewSet(viewsets.ModelViewSet):
    queryset = ItemWorkRelation.objects.all()
    serializer_class = ItemWorkRelationSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class MaterialDetailsViewSet(viewsets.ModelViewSet):
    queryset = MaterialDetails.objects.all()
    serializer_class = MaterialDetailsSerializer


class PersonItemRelationViewSet(viewsets.ModelViewSet):
    queryset = PersonItemRelation.objects.all()
    serializer_class = PersonItemRelationSerializer


class PersonItemRelationRoleViewSet(viewsets.ModelViewSet):
    queryset = PersonItemRelationRole.objects.all()
    serializer_class = PersonItemRelationRoleSerializer


class PublicationViewSet(viewsets.ModelViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class WorkViewSet(viewsets.ModelViewSet):
    queryset = Work.objects.all()
    serializer_class = WorkSerializer


class WorkAuthorViewSet(viewsets.ModelViewSet):
    queryset = WorkAuthor.objects.all()
    serializer_class = WorkAuthorSerializer


class WorkSubjectViewSet(viewsets.ModelViewSet):
    queryset = WorkSubject.objects.all()
    serializer_class = WorkSubjectSerializer
