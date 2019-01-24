from rest_framework import viewsets
from ..serializers import *


class CatalogueViewSet(viewsets.ModelViewSet):
    queryset = Catalogue.objects.all()
    serializer_class = CatalogueSerializer
    http_method_names = ['get']


class CatalogueTypeViewSet(viewsets.ModelViewSet):
    queryset = CatalogueType.objects.all()
    serializer_class = CatalogueTypeSerializer
    http_method_names = ['get']


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    http_method_names = ['get']


class LotViewSet(viewsets.ModelViewSet):
    queryset = Lot.objects.all()
    serializer_class = LotSerializer
    http_method_names = ['get']


class PersonCatalogueRelationViewSet(viewsets.ModelViewSet):
    queryset = PersonCatalogueRelation.objects.all()
    serializer_class = PersonCatalogueRelationSerializer
    http_method_names = ['get']


class PersonCatalogueRelationRoleViewSet(viewsets.ModelViewSet):
    queryset = PersonCatalogueRelationRole.objects.all()
    serializer_class = PersonCatalogueRelationRoleSerializer
    http_method_names = ['get']


class PersonCollectionRelationViewSet(viewsets.ModelViewSet):
    queryset = PersonCollectionRelation.objects.all()
    serializer_class = PersonCollectionRelationSerializer
    http_method_names = ['get']


class CollectionYearViewSet(viewsets.ModelViewSet):
    queryset = CollectionYear.objects.all()
    serializer_class = CollectionYearSerializer
    http_method_names = ['get']


class LibraryViewSet(viewsets.ModelViewSet):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    http_method_names = ['get']


class CatalogueCatalogueTypeRelationViewSet(viewsets.ModelViewSet):
    queryset = CatalogueCatalogueTypeRelation.objects.all()
    serializer_class = CatalogueCatalogueTypeRelationSerializer
    http_method_names = ['get']


class CatalogueHeldByViewSet(viewsets.ModelViewSet):
    queryset = CatalogueHeldBy.objects.all()
    serializer_class = CatalogueHeldBySerializer
    http_method_names = ['get']


class ParisianCategoryViewSet(viewsets.ModelViewSet):
    queryset = ParisianCategory.objects.all()
    serializer_class = ParisianCategorySerializer
    http_method_names = ['get']


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ['get']
