from rest_framework import viewsets
from items.serializers import *


class BindingMaterialDetailsViewSet(viewsets.ModelViewSet):
    queryset = BindingMaterialDetails.objects.all()
    serializer_class = BindingMaterialDetailsSerializer


class BindingMaterialDetailsEquivalentViewSet(viewsets.ModelViewSet):
    queryset = BindingMaterialDetailsEquivalent.objects.all()
    serializer_class = BindingMaterialDetailsEquivalentSerializer


class BookFormatViewSet(viewsets.ModelViewSet):
    queryset = BookFormat.objects.all()
    serializer_class = BookFormatSerializer


class BookFormatEquivalentViewSet(viewsets.ModelViewSet):
    queryset = BookFormatEquivalent.objects.all()
    serializer_class = BookFormatEquivalentSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class CatalogueViewSet(viewsets.ModelViewSet):
    queryset = Catalogue.objects.all()
    serializer_class = CatalogueSerializer


class LotViewSet(viewsets.ModelViewSet):
    queryset = Lot.objects.all()
    serializer_class = LotSerializer


class CatalogueTypeViewSet(viewsets.ModelViewSet):
    queryset = CatalogueType.objects.all()
    serializer_class = CatalogueTypeSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class PersonItemRelationViewSet(viewsets.ModelViewSet):
    queryset = PersonItemRelation.objects.all()
    serializer_class = PersonItemRelationSerializer


class PersonItemRelationRoleViewSet(viewsets.ModelViewSet):
    queryset = PersonItemRelationRole.objects.all()
    serializer_class = PersonItemRelationRoleSerializer


class PersonCatalogueRelationViewSet(viewsets.ModelViewSet):
    queryset = PersonCatalogueRelation.objects.all()
    serializer_class = PersonCatalogueRelationSerializer


class PersonCatalogueRelationRoleViewSet(viewsets.ModelViewSet):
    queryset = PersonCatalogueRelationRole.objects.all()
    serializer_class = PersonCatalogueRelationRoleSerializer


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer


class PlaceEquivalentViewSet(viewsets.ModelViewSet):
    queryset = PlaceEquivalent.objects.all()
    serializer_class = PlaceEquivalentSerializer


class PlaceTypeViewSet(viewsets.ModelViewSet):
    queryset = PlaceType.objects.all()
    serializer_class = PlaceTypeSerializer


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class PublisherEquivalentViewSet(viewsets.ModelViewSet):
    queryset = PublisherEquivalent.objects.all()
    serializer_class = PublisherEquivalentSerializer


class TitleWorkViewSet(viewsets.ModelViewSet):
    queryset = TitleWork.objects.all()
    serializer_class = TitleWorkSerializer
