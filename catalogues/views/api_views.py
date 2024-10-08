from django.http import Http404
from rest_framework import viewsets, filters
from ..serializers import *


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    http_method_names = ['get']
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    http_method_names = ['get']
    filter_backends = [filters.SearchFilter]
    search_fields = ['short_title']

    filter_fields = ['short_title', 'year_of_publication']

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Collection.objects.all()
        for param, value in self.request.query_params.items():
            if param.split('__')[0] in self.filter_fields:
                queryset = queryset.filter(**{param: value})
            else:
                raise Http404
        return queryset


class CollectionTypeViewSet(viewsets.ModelViewSet):
    queryset = CollectionType.objects.all()
    serializer_class = CollectionTypeSerializer
    http_method_names = ['get']


class CatalogueViewSet(viewsets.ModelViewSet):
    queryset = Catalogue.objects.all()
    serializer_class = CatalogueSerializer
    http_method_names = ['get']
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class LotViewSet(viewsets.ModelViewSet):
    queryset = Lot.objects.all()
    serializer_class = LotSerializer
    http_method_names = ['get']


class PersonCollectionRelationViewSet(viewsets.ModelViewSet):
    queryset = PersonCollectionRelation.objects.all()
    serializer_class = PersonCollectionRelationSerializer
    http_method_names = ['get']


class PersonCollectionRelationRoleViewSet(viewsets.ModelViewSet):
    queryset = PersonCollectionRelationRole.objects.all()
    serializer_class = PersonCollectionRelationRoleSerializer
    http_method_names = ['get']


class PersonCatalogueRelationViewSet(viewsets.ModelViewSet):
    queryset = PersonCatalogueRelation.objects.all()
    serializer_class = PersonCatalogueRelationSerializer
    http_method_names = ['get']


class CatalogueYearViewSet(viewsets.ModelViewSet):
    queryset = CatalogueYear.objects.all()
    serializer_class = CatalogueYearSerializer
    http_method_names = ['get']


class LibraryViewSet(viewsets.ModelViewSet):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    http_method_names = ['get']


class CollectionCollectionTypeRelationViewSet(viewsets.ModelViewSet):
    queryset = CollectionCollectionTypeRelation.objects.all()
    serializer_class = CollectionCollectionTypeRelationSerializer
    http_method_names = ['get']


class CollectionHeldByViewSet(viewsets.ModelViewSet):
    queryset = CollectionHeldBy.objects.all()
    serializer_class = CollectionHeldBySerializer
    http_method_names = ['get']


class ParisianCategoryViewSet(viewsets.ModelViewSet):
    queryset = ParisianCategory.objects.all()
    serializer_class = ParisianCategorySerializer
    http_method_names = ['get']


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ['get']
