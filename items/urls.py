from django.urls import path
from django.views.generic import RedirectView
from django_filters.views import FilterView
from django.contrib.auth.decorators import login_required, permission_required
from items.views import *

urlpatterns = [
    path(r'', RedirectView.as_view(url='catalogues/')),
    path(r'catalogues/', login_required(FilterView.as_view(filterset_class=CatalogueFilter)), name="catalogues"),
    path(r'catalogues/<int:pk>', login_required(CatalogueDetailView.as_view()), name="catalogue_detail"),
    path(r'catalogueentries/', login_required(CatalogueEntryListView.as_view()), name="catalogueentries"),
    path(r'bookitems/', login_required(BookitemListView.as_view()), name="bookitems"),

    # Edit forms
    path(r'catalogues/edit/<int:pk>', permission_required('items.change_catalogue')(change_catalogue),
         name="change_catalogue"),
    path(r'catalogues/add', permission_required('items.add_catalogue')(add_catalogue),
         name="add_catalogue"),
    path(r'catalogues/delete/<int:pk>', permission_required('items.delete_catalogue')(delete_catalogue),
         name="delete_catalogue")
]