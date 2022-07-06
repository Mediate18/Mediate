from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required, permission_required
from .views.views import *

urlpatterns = [
    path(r'', RedirectView.as_view(url='transcriptions/')),

    # DocumentScan urls
    path('documentscans/', permission_required('global.view_all')(DocumentScanTableView.as_view()), name='documentscans'),
    path(r'documentscans/<uuid:pk>', permission_required('global.view_all')(DocumentScanDetailView.as_view()),
         name="documentscan_detail"),
    path(r'documentscans/add', permission_required('transcriptions.add_documentscan')(DocumentScanCreateView.as_view()),
         name="add_documentscan"),
    path(r'documentscans/edit/<uuid:pk>',
         permission_required('transcriptions.change_documentscan')(DocumentScanUpdateView.as_view()),
         name="change_documentscan"),
    path(r'documentscans/delete/<uuid:pk>',
         permission_required('transcriptions.delete_documentscan')(DocumentScanDeleteView.as_view()),
         name="delete_documentscan"),

    # SourceMaterial urls
    path('sourcematerials/', permission_required('global.view_all')(SourceMaterialTableView.as_view()), name='sourcematerials'),
    path(r'sourcematerials/<uuid:pk>', permission_required('global.view_all')(SourceMaterialDetailView.as_view()),
         name="sourcematerial_detail"),
    path(r'sourcematerials/add', permission_required('transcriptions.add_sourcematerial')(SourceMaterialCreateView.as_view()),
         name="add_sourcematerial"),
    path(r'sourcematerials/edit/<uuid:pk>',
         permission_required('transcriptions.change_sourcematerial')(SourceMaterialUpdateView.as_view()),
         name="change_sourcematerial"),
    path(r'sourcematerials/delete/<uuid:pk>',
         permission_required('transcriptions.delete_sourcematerial')(SourceMaterialDeleteView.as_view()),
         name="delete_sourcematerial"),

    # ShelfMark urls
    path('shelfmark/', permission_required('global.view_all')(ShelfMarkTableView.as_view()), name='shelfmarks'),
    path(r'shelfmarks/<uuid:pk>', permission_required('global.view_all')(ShelfMarkDetailView.as_view()),
         name="shelfmark_detail"),
    path(r'shelfmarks/add', permission_required('transcriptions.add_shelfmark')(ShelfMarkCreateView.as_view()),
         name="add_shelfmark"),
    path(r'shelfmarks/edit/<uuid:pk>',
         permission_required('transcriptions.change_shelfmark')(ShelfMarkUpdateView.as_view()),
         name="change_shelfmark"),
    path(r'shelfmarks/delete/<uuid:pk>',
         permission_required('transcriptions.delete_shelfmark')(ShelfMarkDeleteView.as_view()),
         name="delete_shelfmark"),

]