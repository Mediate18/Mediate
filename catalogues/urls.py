from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required, permission_required
from .views.views import *

urlpatterns = [
    path(r'', RedirectView.as_view(url='catalogues/')),
    path(r'catalogues/', login_required(CatalogueTableView.as_view()), name="catalogues"),
    path(r'catalogues/<int:pk>', login_required(CatalogueDetailView.as_view()), name="catalogue_detail"),
    # path(r'lots/', login_required(LotListView.as_view()), name="lots"),
    # path(r'lots/<int:pk>', RedirectView.as_view(url=reverse_lazy('lots')), name="lot_detail"),  # TODO

    # Edit forms
    path(r'catalogues/edit/<int:pk>', permission_required('catalogues.change_catalogue')(change_catalogue),
         name="change_catalogue"),
    path(r'catalogues/add', permission_required('catalogues.add_catalogue')(add_catalogue),
         name="add_catalogue"),
    path(r'catalogues/delete/<int:pk>', permission_required('catalogues.delete_catalogue')(delete_catalogue),
         name="delete_catalogue")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)