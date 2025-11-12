from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required, permission_required
from .views.views import *

urlpatterns = [
    path(r'', RedirectView.as_view(url='collections/')),

    path(r'collections/statistics', CollectionStatisticsView.as_view(),
         name='collection_statistics'),
    path(r'collections/chart', get_collections_chart, name='get_collection_chart'),
    path(r'collections/country_chart', get_collection_country_chart,
         name='get_collection_country_chart'),
    path(r'collections/language_chart', get_collection_language_chart,
         name='get_collection_language_chart'),
    path(r'collections/parisian_category_chart', get_collection_parisian_category_chart,
         name='get_collection_parisian_category_chart'),
    path(r'collections/format_chart', get_collection_format_chart,
         name='get_collection_format_chart'),
    path(r'collections/author_gender_chart', get_collection_author_gender_chart,
         name='get_collection_author_gender_chart'),
    path(r'collections/city_chart', get_collection_city_chart,
         name='get_collection_city_chart'),


    # Collection urls
    path('collections/', CollectionTableView.as_view(), name='collections'),
    path(r'collections/<uuid:pk>', CollectionDetailView.as_view(),
       name="collection_detail"),
    path(r'collections/bare/<uuid:pk>', CollectionDetailBareView.as_view(),
       name="collection_detail_bare"),
    path(r'collections/add', permission_required('catalogues.add_collection')(CollectionCreateView.as_view()),
       name="add_collection"),
    path(r'collections/edit/<uuid:pk>',
       permission_required('catalogues.change_collection')(CollectionUpdateView.as_view()),
       name="change_collection"),
    path(r'collections/delete/<uuid:pk>',
       permission_required('catalogues.delete_collection')(CollectionDeleteView.as_view()),
       name="delete_collection"),
    path('collections/map', CollectionLocationMapView.as_view(),
         name='collectionsmap'),
    path(r'previouslot/<uuid:pk>/<int:index>', previous_lot_view,
         name='get_previous_lot'),


    # CollectionHeldBy urls
    path('collectionheldbys/', CollectionHeldByTableView.as_view(), name='collectionheldbys'),
    path(r'collectionheldbys/<uuid:pk>', CollectionHeldByDetailView.as_view(),
       name="collectionheldby_detail"),
    path(r'collectionheldbys/add', permission_required('catalogues.add_collectionheldby')(CollectionHeldByCreateView.as_view()),
       name="add_collectionheldby"),
    path(r'collectionheldbys/edit/<uuid:pk>',
       permission_required('catalogues.change_collectionheldby')(CollectionHeldByUpdateView.as_view()),
       name="change_collectionheldby"),
    path(r'collectionheldbys/delete/<uuid:pk>',
       permission_required('catalogues.delete_collectionheldby')(CollectionHeldByDeleteView.as_view()),
       name="delete_collectionheldby"),


    # CollectionType urls
    path('collectiontypes/', CollectionTypeTableView.as_view(), name='collectiontypes'),
    path(r'collectiontypes/<uuid:pk>', CollectionTypeDetailView.as_view(),
       name="collectiontype_detail"),
    path(r'collectiontypes/add', permission_required('catalogues.add_collectiontype')(CollectionTypeCreateView.as_view()),
       name="add_collectiontype"),
    path(r'collectiontypes/edit/<uuid:pk>',
       permission_required('catalogues.change_collectiontype')(CollectionTypeUpdateView.as_view()),
       name="change_collectiontype"),
    path(r'collectiontypes/delete/<uuid:pk>',
       permission_required('catalogues.delete_collectiontype')(CollectionTypeDeleteView.as_view()),
       name="delete_collectiontype"),


    # CollectionCollectionTypeRelation urls
    path('collectioncollectiontyperelations/', CollectionCollectionTypeRelationTableView.as_view(),
         name='collectioncollectiontyperelations'),
    path(r'collectioncollectiontyperelations/<uuid:pk>',
         CollectionCollectionTypeRelationDetailView.as_view(),
       name="collectioncollectiontyperelation_detail"),
    path(r'collectioncollectiontyperelations/add', permission_required('catalogues.add_collectioncollectiontyperelation')(CollectionCollectionTypeRelationCreateView.as_view()),
       name="add_collectioncollectiontyperelation"),
    path(r'collectioncollectiontyperelations/edit/<uuid:pk>',
       permission_required('catalogues.change_collectioncollectiontyperelation')(CollectionCollectionTypeRelationUpdateView.as_view()),
       name="change_collectioncollectiontyperelation"),
    path(r'collectioncollectiontyperelations/delete/<uuid:pk>',
       permission_required('catalogues.delete_collectioncollectiontyperelation')(CollectionCollectionTypeRelationDeleteView.as_view()),
       name="delete_collectioncollectiontyperelation"),


    # Catalogue urls
    path('catalogues/', CatalogueTableView.as_view(), name='catalogues'),
    path(r'catalogues/<uuid:pk>', CatalogueDetailView.as_view(),
       name="catalogue_detail"),
    path(r'catalogues/add', permission_required('catalogues.add_catalogue')(CatalogueCreateView.as_view()),
       name="add_catalogue"),
    path(r'catalogues/edit/<uuid:pk>',
       permission_required('catalogues.change_catalogue')(CatalogueUpdateView.as_view()),
       name="change_catalogue"),
    path(r'catalogues/delete/<uuid:pk>',
       permission_required('catalogues.delete_catalogue')(CatalogueDeleteView.as_view()),
       name="delete_catalogue"),


    # CatalogueYear urls
    path('catalogueyears/', CatalogueYearTableView.as_view(), name='catalogueyears'),
    path(r'catalogueyears/<uuid:pk>', CatalogueYearDetailView.as_view(),
       name="catalogueyear_detail"),
    path(r'catalogueyears/add', permission_required('catalogues.add_catalogueyear')(CatalogueYearCreateView.as_view()),
       name="add_catalogueyear"),
    path(r'catalogueyears/edit/<uuid:pk>',
       permission_required('catalogues.change_catalogueyear')(CatalogueYearUpdateView.as_view()),
       name="change_catalogueyear"),
    path(r'catalogueyears/delete/<uuid:pk>',
       permission_required('catalogues.delete_catalogueyear')(CatalogueYearDeleteView.as_view()),
       name="delete_catalogueyear"),


    # Library urls
    path('libraries/', LibraryTableView.as_view(), name='libraries'),
    path(r'libraries/<uuid:pk>', LibraryDetailView.as_view(),
       name="library_detail"),
    path(r'libraries/add', permission_required('catalogues.add_library')(LibraryCreateView.as_view()),
       name="add_library"),
    path(r'libraries/edit/<uuid:pk>',
       permission_required('catalogues.change_library')(LibraryUpdateView.as_view()),
       name="change_library"),
    path(r'libraries/delete/<uuid:pk>',
       permission_required('catalogues.delete_library')(LibraryDeleteView.as_view()),
       name="delete_library"),


    # Lot urls
    path('lots/', LotTableView.as_view(), name='lots'),
    path(r'lots/<uuid:pk>', LotDetailView.as_view(),
       name="lot_detail"),
    path(r'lots/add', permission_required('catalogues.add_lot')(LotCreateView.as_view()),
       name="add_lot"),
    path(r'lots/edit/<uuid:pk>',
       permission_required('catalogues.change_lot')(LotUpdateView.as_view()),
       name="change_lot"),
    path(r'lots/delete/<uuid:pk>',
       permission_required('catalogues.delete_lot')(LotDeleteView.as_view()),
       name="delete_lot"),
    path(r'lots/expand/<uuid:pk>', permission_required('items.add_item')(expand_lot_view), name="expand_lot"),
    path(r'lots/add_before/<uuid:pk>', permission_required('catalogues.add_lot')(add_lot_before), name="add_lot_before"),
    path(r'lots/add_at_end/<uuid:pk>', permission_required('catalogues.add_lot')(add_lot_at_end), name="add_lot_at_end"),


    # PersonCollectionRelation urls
    path('personcollectionrelations/', PersonCollectionRelationTableView.as_view(), name='personcollectionrelations'),
    path(r'personcollectionrelations/<uuid:pk>', PersonCollectionRelationDetailView.as_view(),
       name="personcollectionrelation_detail"),
    path(r'personcollectionrelations/add', permission_required('catalogues.add_personcollectionrelation')(PersonCollectionRelationCreateView.as_view()),
       name="add_personcollectionrelation"),
    path(r'personcollectionrelations/edit/<uuid:pk>',
       permission_required('catalogues.change_personcollectionrelation')(PersonCollectionRelationUpdateView.as_view()),
       name="change_personcollectionrelation"),
    path(r'personcollectionrelations/delete/<uuid:pk>',
       permission_required('catalogues.delete_personcollectionrelation')(PersonCollectionRelationDeleteView.as_view()),
       name="delete_personcollectionrelation"),


    # PersonCollectionRelationRole urls
    path('personcollectionrelationroles/', PersonCollectionRelationRoleTableView.as_view(), name='personcollectionrelationroles'),
    path(r'personcollectionrelationroles/<uuid:pk>', PersonCollectionRelationRoleDetailView.as_view(),
       name="personcollectionrelationrole_detail"),
    path(r'personcollectionrelationroles/add', permission_required('catalogues.add_personcollectionrelationrole')(PersonCollectionRelationRoleCreateView.as_view()),
       name="add_personcollectionrelationrole"),
    path(r'personcollectionrelationroles/edit/<uuid:pk>',
       permission_required('catalogues.change_personcollectionrelationrole')(PersonCollectionRelationRoleUpdateView.as_view()),
       name="change_personcollectionrelationrole"),
    path(r'personcollectionrelationroles/delete/<uuid:pk>',
       permission_required('catalogues.delete_personcollectionrelationrole')(PersonCollectionRelationRoleDeleteView.as_view()),
       name="delete_personcollectionrelationrole"),


    # PersonCatalogueRelation urls
    path('personcataloguerelations/', PersonCatalogueRelationTableView.as_view(), name='personcataloguerelations'),
    path(r'personcataloguerelations/<uuid:pk>', PersonCatalogueRelationDetailView.as_view(),
       name="personcataloguerelation_detail"),
    path(r'personcataloguerelations/add', permission_required('catalogues.add_personcataloguerelation')(PersonCatalogueRelationCreateView.as_view()),
       name="add_personcataloguerelation"),
    path(r'personcataloguerelations/edit/<uuid:pk>',
       permission_required('catalogues.change_personcataloguerelation')(PersonCatalogueRelationUpdateView.as_view()),
       name="change_personcataloguerelation"),
    path(r'personcataloguerelations/delete/<uuid:pk>',
       permission_required('catalogues.delete_personcataloguerelation')(PersonCatalogueRelationDeleteView.as_view()),
       name="delete_personcataloguerelation"),


    # CollectionPlaceRelation urls
    path('collectionplacerelations/', CollectionPlaceRelationTableView.as_view(), name='collectionplacerelations'),
    path(r'collectionplacerelations/<uuid:pk>', CollectionPlaceRelationDetailView.as_view(),
         name="collectionplacerelation_detail"),
    path(r'collectionplacerelations/add', permission_required('catalogues.add_collectionplacerelation')(CollectionPlaceRelationCreateView.as_view()),
         name="add_collectionplacerelation"),
    path(r'collectionplacerelations/edit/<uuid:pk>',
         permission_required('catalogues.change_collectionplacerelation')(CollectionPlaceRelationUpdateView.as_view()),
         name="change_collectionplacerelation"),
    path(r'collectionplacerelations/delete/<uuid:pk>',
         permission_required('catalogues.delete_collectionplacerelation')(CollectionPlaceRelationDeleteView.as_view()),
         name="delete_collectionplacerelation"),


    # Category urls
    path('categories/', CategoryTableView.as_view(), name='categories'),
    path(r'categories/<uuid:pk>', CategoryDetailView.as_view(),
       name="category_detail"),
    path(r'categories/add', permission_required('catalogues.add_category')(CategoryCreateView.as_view()),
       name="add_category"),
    path(r'categories/edit/<uuid:pk>',
       permission_required('catalogues.change_category')(CategoryUpdateView.as_view()),
       name="change_category"),
    path(r'categories/delete/<uuid:pk>',
       permission_required('catalogues.delete_category')(CategoryDeleteView.as_view()),
       name="delete_category"),


    # ParisianCategory urls
    path('parisiancategories/', ParisianCategoryTableView.as_view(), name='parisiancategories'),
    path(r'parisiancategories/<uuid:pk>', ParisianCategoryDetailView.as_view(),
       name="parisiancategory_detail"),
    path(r'parisiancategories/add', permission_required('catalogues.add_parisiancategory')(ParisianCategoryCreateView.as_view()),
       name="add_parisiancategory"),
    path(r'parisiancategories/edit/<uuid:pk>',
       permission_required('catalogues.change_parisiancategory')(ParisianCategoryUpdateView.as_view()),
       name="change_parisiancategory"),
    path(r'parisiancategories/delete/<uuid:pk>',
       permission_required('catalogues.delete_parisiancategory')(ParisianCategoryDeleteView.as_view()),
       name="delete_parisiancategory"),


    # CollectionPlaceRelationType urls
    path('collectionplacerelationtypes/', CollectionPlaceRelationTypeTableView.as_view(), name='collectionplacerelationtypes'),
    path(r'collectionplacerelationtypes/<uuid:pk>', CollectionPlaceRelationTypeDetailView.as_view(),
       name="collectionplacerelationtype_detail"),
    path(r'collectionplacerelationtypes/add', permission_required('catalogues.add_collectionplacerelationtype')(CollectionPlaceRelationTypeCreateView.as_view()),
       name="add_collectionplacerelationtype"),
    path(r'collectionplacerelationtypes/edit/<uuid:pk>',
       permission_required('catalogues.change_collectionplacerelationtype')(CollectionPlaceRelationTypeUpdateView.as_view()),
       name="change_collectionplacerelationtype"),
    path(r'collectionplacerelationtypes/delete/<uuid:pk>',
       permission_required('catalogues.delete_collectionplacerelationtype')(CollectionPlaceRelationTypeDeleteView.as_view()),
       name="delete_collectionplacerelationtype"),

    # Person-Work correlation
    path('personworkcorrelation/', person_work_correlation, name="personworkcorrelation"),
    path('personworkcorrelationlist/', person_work_correlation_list, name="personworkcorrelationlist"),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)