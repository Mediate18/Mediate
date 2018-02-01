from django.urls import path
from django.views.generic import RedirectView
from django_filters.views import FilterView
from django.contrib.auth.decorators import login_required
from items.views import *

urlpatterns = [
    path(r'', RedirectView.as_view(url='catalogues/')),
    path(r'catalogues/', login_required(FilterView.as_view(filterset_class=CatalogueFilter)), name="catalogues"),
    path(r'catalogues/<int:pk>', login_required(CatalogueDetailView.as_view()), name="catalogue_detail"),
    path(r'catalogueitems/', login_required(CatalogueItemListView.as_view()), name="catalogueitems"),
    path(r'bookitems/', login_required(BookitemListView.as_view()), name="bookitems"),
]