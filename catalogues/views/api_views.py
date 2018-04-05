from rest_framework import viewsets
from ..serializers import *


class CatalogueViewSet(viewsets.ModelViewSet):
    queryset = Catalogue.objects.all()
    serializer_class = CatalogueSerializer


class CatalogueTypeViewSet(viewsets.ModelViewSet):
    queryset = CatalogueType.objects.all()
    serializer_class = CatalogueTypeSerializer


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer


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