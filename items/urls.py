from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django_filters.views import FilterView
from django.contrib.auth.decorators import login_required, permission_required
from items.views import *

urlpatterns = [
    path(r'', RedirectView.as_view(url='catalogues/')),
    path(r'catalogues/', login_required(CatalogueTableView.as_view()), name="catalogues"),
    path(r'catalogues/<int:pk>', login_required(CatalogueDetailView.as_view()), name="catalogue_detail"),
    path(r'catalogueentries/', login_required(LotListView.as_view()), name="catalogueentries"),
    path(r'items/', login_required(ItemListView.as_view()), name="items"),

    # Edit forms
    path(r'catalogues/edit/<int:pk>', permission_required('items.change_catalogue')(change_catalogue),
         name="change_catalogue"),
    path(r'catalogues/add', permission_required('items.add_catalogue')(add_catalogue),
         name="add_catalogue"),
    path(r'catalogues/delete/<int:pk>', permission_required('items.delete_catalogue')(delete_catalogue),
         name="delete_catalogue")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)