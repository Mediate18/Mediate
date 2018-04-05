from rest_framework import viewsets
from items.serializers import *


class BindingMaterialDetailsViewSet(viewsets.ModelViewSet):
    queryset = BindingMaterialDetails.objects.all()
    serializer_class = BindingMaterialDetailsSerializer


class BookFormatViewSet(viewsets.ModelViewSet):
    queryset = BookFormat.objects.all()
    serializer_class = BookFormatSerializer


class CatalogueViewSet(viewsets.ModelViewSet):
    queryset = Catalogue.objects.all()
    serializer_class = CatalogueSerializer


class CatalogueTypeViewSet(viewsets.ModelViewSet):
    queryset = CatalogueType.objects.all()
    serializer_class = CatalogueTypeSerializer


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class LotViewSet(viewsets.ModelViewSet):
    queryset = Lot.objects.all()
    serializer_class = LotSerializer


class PersonCatalogueRelationViewSet(viewsets.ModelViewSet):
    queryset = PersonCatalogueRelation.objects.all()
    serializer_class = PersonCatalogueRelationSerializer


class PersonCatalogueRelationRoleViewSet(viewsets.ModelViewSet):
    queryset = PersonCatalogueRelationRole.objects.all()
    serializer_class = PersonCatalogueRelationRoleSerializer


class PersonCollectionRelationViewSet(viewsets.ModelViewSet):
    queryset = PersonCollectionRelation.objects.all()
    serializer_class = PersonCollectionRelationSerializer


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
