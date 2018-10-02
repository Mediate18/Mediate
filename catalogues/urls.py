from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required, permission_required
from .views.views import *

urlpatterns = [
    path(r'', RedirectView.as_view(url='catalogues/')),

    # Catalogue urls
    path('catalogues/', login_required(CatalogueTableView.as_view()), name='catalogues'),
    path(r'catalogues/<uuid:pk>', login_required(CatalogueDetailView.as_view()),
       name="catalogue_detail"),
    path(r'catalogues/bare/<uuid:pk>', login_required(CatalogueDetailBareView.as_view()),
       name="catalogue_detail_bare"),
    path(r'catalogues/add', permission_required('catalogues.add_catalogue')(CatalogueCreateView.as_view()),
       name="add_catalogue"),
    path(r'catalogues/edit/<uuid:pk>',
       permission_required('catalogues.change_catalogue')(CatalogueUpdateView.as_view()),
       name="change_catalogue"),
    path(r'catalogues/delete/<uuid:pk>',
       permission_required('catalogues.delete_catalogue')(CatalogueDeleteView.as_view()),
       name="delete_catalogue"),


    # CatalogueHeldBy urls
    path('catalogueheldbys/', login_required(CatalogueHeldByTableView.as_view()), name='catalogueheldbys'),
    path(r'catalogueheldbys/<uuid:pk>', login_required(CatalogueHeldByDetailView.as_view()),
       name="catalogueheldby_detail"),
    path(r'catalogueheldbys/add', permission_required('catalogues.add_catalogueheldby')(CatalogueHeldByCreateView.as_view()),
       name="add_catalogueheldby"),
    path(r'catalogueheldbys/edit/<uuid:pk>',
       permission_required('catalogues.change_catalogueheldby')(CatalogueHeldByUpdateView.as_view()),
       name="change_catalogueheldby"),
    path(r'catalogueheldbys/delete/<uuid:pk>',
       permission_required('catalogue.delete_catalogueheldby')(CatalogueHeldByDeleteView.as_view()),
       name="delete_catalogueheldby"),


    # CatalogueType urls
    path('cataloguetypes/', login_required(CatalogueTypeTableView.as_view()), name='cataloguetypes'),
    path(r'cataloguetypes/<uuid:pk>', login_required(CatalogueTypeDetailView.as_view()),
       name="cataloguetype_detail"),
    path(r'cataloguetypes/add', permission_required('catalogues.add_cataloguetype')(CatalogueTypeCreateView.as_view()),
       name="add_cataloguetype"),
    path(r'cataloguetypes/edit/<uuid:pk>',
       permission_required('catalogues.change_cataloguetype')(CatalogueTypeUpdateView.as_view()),
       name="change_cataloguetype"),
    path(r'cataloguetypes/delete/<uuid:pk>',
       permission_required('catalogue.delete_cataloguetype')(CatalogueTypeDeleteView.as_view()),
       name="delete_cataloguetype"),


    # Collection urls
    path('collections/', login_required(CollectionTableView.as_view()), name='collections'),
    path(r'collections/<uuid:pk>', login_required(CollectionDetailView.as_view()),
       name="collection_detail"),
    path(r'collections/add', permission_required('catalogues.add_collection')(CollectionCreateView.as_view()),
       name="add_collection"),
    path(r'collections/edit/<uuid:pk>',
       permission_required('catalogues.change_collection')(CollectionUpdateView.as_view()),
       name="change_collection"),
    path(r'collections/delete/<uuid:pk>',
       permission_required('catalogue.delete_collection')(CollectionDeleteView.as_view()),
       name="delete_collection"),


    # CollectionYear urls
    path('collectionyears/', login_required(CollectionYearTableView.as_view()), name='collectionyears'),
    path(r'collectionyears/<uuid:pk>', login_required(CollectionYearDetailView.as_view()),
       name="collectionyear_detail"),
    path(r'collectionyears/add', permission_required('catalogues.add_collectionyear')(CollectionYearCreateView.as_view()),
       name="add_collectionyear"),
    path(r'collectionyears/edit/<uuid:pk>',
       permission_required('catalogues.change_collectionyear')(CollectionYearUpdateView.as_view()),
       name="change_collectionyear"),
    path(r'collectionyears/delete/<uuid:pk>',
       permission_required('catalogue.delete_collectionyear')(CollectionYearDeleteView.as_view()),
       name="delete_collectionyear"),


    # Library urls
    path('libraries/', login_required(LibraryTableView.as_view()), name='libraries'),
    path(r'libraries/<uuid:pk>', login_required(LibraryDetailView.as_view()),
       name="library_detail"),
    path(r'libraries/add', permission_required('catalogues.add_library')(LibraryCreateView.as_view()),
       name="add_library"),
    path(r'libraries/edit/<uuid:pk>',
       permission_required('catalogues.change_library')(LibraryUpdateView.as_view()),
       name="change_library"),
    path(r'libraries/delete/<uuid:pk>',
       permission_required('catalogue.delete_library')(LibraryDeleteView.as_view()),
       name="delete_library"),


    # Lot urls
    path('lots/', login_required(LotTableView.as_view()), name='lots'),
    path(r'lots/<uuid:pk>', login_required(LotDetailView.as_view()),
       name="lot_detail"),
    path(r'lots/add', permission_required('catalogues.add_lot')(LotCreateView.as_view()),
       name="add_lot"),
    path(r'lots/edit/<uuid:pk>',
       permission_required('catalogues.change_lot')(LotUpdateView.as_view()),
       name="change_lot"),
    path(r'lots/delete/<uuid:pk>',
       permission_required('catalogue.delete_lot')(LotDeleteView.as_view()),
       name="delete_lot"),


    # PersonCatalogueRelation urls
    path('personcataloguerelations/', login_required(PersonCatalogueRelationTableView.as_view()), name='personcataloguerelations'),
    path(r'personcataloguerelations/<uuid:pk>', login_required(PersonCatalogueRelationDetailView.as_view()),
       name="personcataloguerelation_detail"),
    path(r'personcataloguerelations/add', permission_required('catalogues.add_personcataloguerelation')(PersonCatalogueRelationCreateView.as_view()),
       name="add_personcataloguerelation"),
    path(r'personcataloguerelations/edit/<uuid:pk>',
       permission_required('catalogues.change_personcataloguerelation')(PersonCatalogueRelationUpdateView.as_view()),
       name="change_personcataloguerelation"),
    path(r'personcataloguerelations/delete/<uuid:pk>',
       permission_required('catalogue.delete_personcataloguerelation')(PersonCatalogueRelationDeleteView.as_view()),
       name="delete_personcataloguerelation"),


    # PersonCatalogueRelationRole urls
    path('personcataloguerelationroles/', login_required(PersonCatalogueRelationRoleTableView.as_view()), name='personcataloguerelationroles'),
    path(r'personcataloguerelationroles/<uuid:pk>', login_required(PersonCatalogueRelationRoleDetailView.as_view()),
       name="personcataloguerelationrole_detail"),
    path(r'personcataloguerelationroles/add', permission_required('catalogues.add_personcataloguerelationrole')(PersonCatalogueRelationRoleCreateView.as_view()),
       name="add_personcataloguerelationrole"),
    path(r'personcataloguerelationroles/edit/<uuid:pk>',
       permission_required('catalogues.change_personcataloguerelationrole')(PersonCatalogueRelationRoleUpdateView.as_view()),
       name="change_personcataloguerelationrole"),
    path(r'personcataloguerelationroles/delete/<uuid:pk>',
       permission_required('catalogue.delete_personcataloguerelationrole')(PersonCatalogueRelationRoleDeleteView.as_view()),
       name="delete_personcataloguerelationrole"),


    # PersonCollectionRelation urls
    path('personcollectionrelations/', login_required(PersonCollectionRelationTableView.as_view()), name='personcollectionrelations'),
    path(r'personcollectionrelations/<uuid:pk>', login_required(PersonCollectionRelationDetailView.as_view()),
       name="personcollectionrelation_detail"),
    path(r'personcollectionrelations/add', permission_required('catalogues.add_personcollectionrelation')(PersonCollectionRelationCreateView.as_view()),
       name="add_personcollectionrelation"),
    path(r'personcollectionrelations/edit/<uuid:pk>',
       permission_required('catalogues.change_personcollectionrelation')(PersonCollectionRelationUpdateView.as_view()),
       name="change_personcollectionrelation"),
    path(r'personcollectionrelations/delete/<uuid:pk>',
       permission_required('catalogue.delete_personcollectionrelation')(PersonCollectionRelationDeleteView.as_view()),
       name="delete_personcollectionrelation"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)