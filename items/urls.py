from django.urls import path
from django_filters.views import FilterView
from items.views import *

urlpatterns = [
    path(r'catalogues/', FilterView.as_view(filterset_class=CatalogueFilter), name="catalogues"),
    path(r'catalogues/<int:pk>', CatalogueDetailView.as_view(), name="catalogue_detail"),
    path(r'catalogueitems/', CatalogueItemListView.as_view(), name="catalogueitems"),
    path(r'bookitems/', BookitemListView.as_view(), name="bookitems"),
]