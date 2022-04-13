from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required, permission_required
from .views.views import *

urlpatterns = [
    path(r'', RedirectView.as_view(url='collections/')),

    # Collection urls
    path('collections/', permission_required('global.view_all')(CollectionTableView.as_view()), name='collections'),
    path(r'collections/<uuid:pk>', permission_required('global.view_all')(CollectionDetailView.as_view()),
       name="collection_detail"),
    path(r'collections/bare/<uuid:pk>', permission_required('global.view_all')(CollectionDetailBareView.as_view()),
       name="collection_detail_bare"),
    path(r'collections/add', permission_required('catalogues.add_collection')(CollectionCreateView.as_view()),
       name="add_collection"),
    path(r'collections/edit/<uuid:pk>',
       permission_required('catalogues.change_collection')(CollectionUpdateView.as_view()),
       name="change_collection"),
    path(r'collections/delete/<uuid:pk>',
       permission_required('catalogues.delete_collection')(CollectionDeleteView.as_view()),
       name="delete_collection"),
    path('collections/map', permission_required('global.view_all')(CollectionLocationMapView.as_view()),
         name='collectionsmap'),
    path(r'previouslot/<uuid:pk>/<int:index>', permission_required('global.view_all')(previous_lot_view),
         name='get_previous_lot'),


    # CollectionHeldBy urls
    path('collectionheldbys/', permission_required('global.view_all')(CollectionHeldByTableView.as_view()), name='collectionheldbys'),
    path(r'collectionheldbys/<uuid:pk>', permission_required('global.view_all')(CollectionHeldByDetailView.as_view()),
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
    path('collectiontypes/', permission_required('global.view_all')(CollectionTypeTableView.as_view()), name='collectiontypes'),
    path(r'collectiontypes/<uuid:pk>', permission_required('global.view_all')(CollectionTypeDetailView.as_view()),
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
    path('collectioncollectiontyperelations/', permission_required('global.view_all')(CollectionCollectionTypeRelationTableView.as_view()),
         name='collectioncollectiontyperelations'),
    path(r'collectioncollectiontyperelations/<uuid:pk>',
         permission_required('global.view_all')(CollectionCollectionTypeRelationDetailView.as_view()),
       name="collectioncollectiontyperelation_detail"),
    path(r'collectioncollectiontyperelations/add', permission_required('catalogues.add_collectioncollectiontyperelation')(CollectionCollectionTypeRelationCreateView.as_view()),
       name="add_collectioncollectiontyperelation"),
    path(r'collectioncollectiontyperelations/edit/<uuid:pk>',
       permission_required('catalogues.change_collectioncollectiontyperelation')(CollectionCollectionTypeRelationUpdateView.as_view()),
       name="change_collectioncollectiontyperelation"),
    path(r'collectioncollectiontyperelations/delete/<uuid:pk>',
       permission_required('catalogues.delete_collectioncollectiontyperelation')(CollectionCollectionTypeRelationDeleteView.as_view()),
       name="delete_collectioncollectiontyperelation"),


    # Collection_TMP urls
    path('collection_tmps/', permission_required('global.view_all')(Collection_TMPTableView.as_view()), name='collection_tmps'),
    path(r'collection_tmps/<uuid:pk>', permission_required('global.view_all')(Collection_TMPDetailView.as_view()),
       name="collection_tmp_detail"),
    path(r'collection_tmps/add', permission_required('catalogues.add_collection_tmp')(Collection_TMPCreateView.as_view()),
       name="add_collection_tmp"),
    path(r'collection_tmps/edit/<uuid:pk>',
       permission_required('catalogues.change_collection_tmp')(Collection_TMPUpdateView.as_view()),
       name="change_collection_tmp"),
    path(r'collection_tmps/delete/<uuid:pk>',
       permission_required('catalogues.delete_collection_tmp')(Collection_TMPDeleteView.as_view()),
       name="delete_collection_tmp"),


    # Collection_TMPYear urls
    path('collection_tmpyears/', permission_required('global.view_all')(Collection_TMPYearTableView.as_view()), name='collection_tmpyears'),
    path(r'collection_tmpyears/<uuid:pk>', permission_required('global.view_all')(Collection_TMPYearDetailView.as_view()),
       name="collection_tmpyear_detail"),
    path(r'collection_tmpyears/add', permission_required('catalogues.add_collection_tmpyear')(Collection_TMPYearCreateView.as_view()),
       name="add_collection_tmpyear"),
    path(r'collection_tmpyears/edit/<uuid:pk>',
       permission_required('catalogues.change_collection_tmpyear')(Collection_TMPYearUpdateView.as_view()),
       name="change_collection_tmpyear"),
    path(r'collection_tmpyears/delete/<uuid:pk>',
       permission_required('catalogues.delete_collection_tmpyear')(Collection_TMPYearDeleteView.as_view()),
       name="delete_collection_tmpyear"),


    # Library urls
    path('libraries/', permission_required('global.view_all')(LibraryTableView.as_view()), name='libraries'),
    path(r'libraries/<uuid:pk>', permission_required('global.view_all')(LibraryDetailView.as_view()),
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
    path('lots/', permission_required('global.view_all')(LotTableView.as_view()), name='lots'),
    path(r'lots/<uuid:pk>', permission_required('global.view_all')(LotDetailView.as_view()),
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
    path('personcollectionrelations/', permission_required('global.view_all')(PersonCollectionRelationTableView.as_view()), name='personcollectionrelations'),
    path(r'personcollectionrelations/<uuid:pk>', permission_required('global.view_all')(PersonCollectionRelationDetailView.as_view()),
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
    path('personcollectionrelationroles/', permission_required('global.view_all')(PersonCollectionRelationRoleTableView.as_view()), name='personcollectionrelationroles'),
    path(r'personcollectionrelationroles/<uuid:pk>', permission_required('global.view_all')(PersonCollectionRelationRoleDetailView.as_view()),
       name="personcollectionrelationrole_detail"),
    path(r'personcollectionrelationroles/add', permission_required('catalogues.add_personcollectionrelationrole')(PersonCollectionRelationRoleCreateView.as_view()),
       name="add_personcollectionrelationrole"),
    path(r'personcollectionrelationroles/edit/<uuid:pk>',
       permission_required('catalogues.change_personcollectionrelationrole')(PersonCollectionRelationRoleUpdateView.as_view()),
       name="change_personcollectionrelationrole"),
    path(r'personcollectionrelationroles/delete/<uuid:pk>',
       permission_required('catalogues.delete_personcollectionrelationrole')(PersonCollectionRelationRoleDeleteView.as_view()),
       name="delete_personcollectionrelationrole"),


    # PersonCollection_TMPRelation urls
    path('personcollection_tmprelations/', permission_required('global.view_all')(PersonCollection_TMPRelationTableView.as_view()), name='personcollection_tmprelations'),
    path(r'personcollection_tmprelations/<uuid:pk>', permission_required('global.view_all')(PersonCollection_TMPRelationDetailView.as_view()),
       name="personcollection_tmprelation_detail"),
    path(r'personcollection_tmprelations/add', permission_required('catalogues.add_personcollection_tmprelation')(PersonCollection_TMPRelationCreateView.as_view()),
       name="add_personcollection_tmprelation"),
    path(r'personcollection_tmprelations/edit/<uuid:pk>',
       permission_required('catalogues.change_personcollection_tmprelation')(PersonCollection_TMPRelationUpdateView.as_view()),
       name="change_personcollection_tmprelation"),
    path(r'personcollection_tmprelations/delete/<uuid:pk>',
       permission_required('catalogues.delete_personcollection_tmprelation')(PersonCollection_TMPRelationDeleteView.as_view()),
       name="delete_personcollection_tmprelation"),


    # CollectionPlaceRelation urls
    path('collectionplacerelations/', permission_required('global.view_all')(CollectionPlaceRelationTableView.as_view()), name='collectionplacerelations'),
    path(r'collectionplacerelations/<uuid:pk>', permission_required('global.view_all')(CollectionPlaceRelationDetailView.as_view()),
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
    path('categories/', permission_required('global.view_all')(CategoryTableView.as_view()), name='categories'),
    path(r'categories/<uuid:pk>', permission_required('global.view_all')(CategoryDetailView.as_view()),
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
    path('parisiancategories/', permission_required('global.view_all')(ParisianCategoryTableView.as_view()), name='parisiancategories'),
    path(r'parisiancategories/<uuid:pk>', permission_required('global.view_all')(ParisianCategoryDetailView.as_view()),
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
    path('collectionplacerelationtypes/', permission_required('global.view_all')(CollectionPlaceRelationTypeTableView.as_view()), name='collectionplacerelationtypes'),
    path(r'collectionplacerelationtypes/<uuid:pk>', permission_required('global.view_all')(CollectionPlaceRelationTypeDetailView.as_view()),
       name="collectionplacerelationtype_detail"),
    path(r'collectionplacerelationtypes/add', permission_required('catalogues.add_collectionplacerelationtype')(CollectionPlaceRelationTypeCreateView.as_view()),
       name="add_collectionplacerelationtype"),
    path(r'collectionplacerelationtypes/edit/<uuid:pk>',
       permission_required('catalogues.change_collectionplacerelationtype')(CollectionPlaceRelationTypeUpdateView.as_view()),
       name="change_collectionplacerelationtype"),
    path(r'collectionplacerelationtypes/delete/<uuid:pk>',
       permission_required('catalogues.delete_collectionplacerelationtype')(CollectionPlaceRelationTypeDeleteView.as_view()),
       name="delete_collectionplacerelationtype"),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)