from rest_framework import viewsets
from items.serializers import *


class CatalogueTypeViewSet(viewsets.ModelViewSet):
    """
    TODO
    """
    queryset = CatalogueType.objects.all()
    serializer_class = CatalogueTypeSerializer


class CatalogueViewSet(viewsets.ModelViewSet):
    """
    TODO
    """
    queryset = Catalogue.objects.all()
    serializer_class = CatalogueSerializer


class CatalogueItemViewSet(viewsets.ModelViewSet):
    """
    TODO
    """
    queryset = CatalogueItem.objects.all()
    serializer_class = CatalogueItemSerializer


class BookItemViewSet(viewsets.ModelViewSet):
    """
    TODO
    """
    queryset = BookItem.objects.all()
    serializer_class = BookItemSerializer