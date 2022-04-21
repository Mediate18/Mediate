from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required, permission_required
from .views.views import *

urlpatterns = [
    path(r'', RedirectView.as_view(url='catalogues/')),

    # Catalogue urls
    path('catalogues/', permission_required('global.view_all')(CatalogueTableView.as_view()), name='catalogues'),
    path(r'catalogues/<uuid:pk>', permission_required('global.view_all')(CatalogueDetailView.as_view()),
       name="catalogue_detail"),
    path(r'catalogues/bare/<uuid:pk>', permission_required('global.view_all')(CatalogueDetailBareView.as_view()),
       name="catalogue_detail_bare"),
    path(r'catalogues/add', permission_required('catalogues.add_catalogue')(CatalogueCreateView.as_view()),
       name="add_catalogue"),
    path(r'catalogues/edit/<uuid:pk>',
       permission_required('catalogues.change_catalogue')(CatalogueUpdateView.as_view()),
       name="change_catalogue"),
    path(r'catalogues/delete/<uuid:pk>',
       permission_required('catalogues.delete_catalogue')(CatalogueDeleteView.as_view()),
       name="delete_catalogue"),
    path('catalogues/map', permission_required('global.view_all')(CatalogueLocationMapView.as_view()),
         name='cataloguesmap'),
    path(r'previouslot/<uuid:pk>/<int:index>', permission_required('global.view_all')(previous_lot_view),
         name='get_previous_lot'),

    path(r'catalogues/statistics', permission_required('global.view_all')(CatalogueStatisticsView.as_view()),
         name='catalogue_statistics'),
    path(r'catalogues/chart', permission_required('global.view_all')(get_catalogues_chart), name='get_catalogue_chart'),
    path(r'catalogues/country_chart', permission_required('global.view_all')(get_catalogue_country_chart),
         name='get_catalogue_country_chart'),


    # CatalogueHeldBy urls
    path('catalogueheldbys/', permission_required('global.view_all')(CatalogueHeldByTableView.as_view()), name='catalogueheldbys'),
    path(r'catalogueheldbys/<uuid:pk>', permission_required('global.view_all')(CatalogueHeldByDetailView.as_view()),
       name="catalogueheldby_detail"),
    path(r'catalogueheldbys/add', permission_required('catalogues.add_catalogueheldby')(CatalogueHeldByCreateView.as_view()),
       name="add_catalogueheldby"),
    path(r'catalogueheldbys/edit/<uuid:pk>',
       permission_required('catalogues.change_catalogueheldby')(CatalogueHeldByUpdateView.as_view()),
       name="change_catalogueheldby"),
    path(r'catalogueheldbys/delete/<uuid:pk>',
       permission_required('catalogues.delete_catalogueheldby')(CatalogueHeldByDeleteView.as_view()),
       name="delete_catalogueheldby"),


    # CatalogueType urls
    path('cataloguetypes/', permission_required('global.view_all')(CatalogueTypeTableView.as_view()), name='cataloguetypes'),
    path(r'cataloguetypes/<uuid:pk>', permission_required('global.view_all')(CatalogueTypeDetailView.as_view()),
       name="cataloguetype_detail"),
    path(r'cataloguetypes/add', permission_required('catalogues.add_cataloguetype')(CatalogueTypeCreateView.as_view()),
       name="add_cataloguetype"),
    path(r'cataloguetypes/edit/<uuid:pk>',
       permission_required('catalogues.change_cataloguetype')(CatalogueTypeUpdateView.as_view()),
       name="change_cataloguetype"),
    path(r'cataloguetypes/delete/<uuid:pk>',
       permission_required('catalogues.delete_cataloguetype')(CatalogueTypeDeleteView.as_view()),
       name="delete_cataloguetype"),


    # CatalogueCatalogueTypeRelation urls
    path('cataloguecataloguetyperelations/', permission_required('global.view_all')(CatalogueCatalogueTypeRelationTableView.as_view()),
         name='cataloguecataloguetyperelations'),
    path(r'cataloguecataloguetyperelations/<uuid:pk>',
         permission_required('global.view_all')(CatalogueCatalogueTypeRelationDetailView.as_view()),
       name="cataloguecataloguetyperelation_detail"),
    path(r'cataloguecataloguetyperelations/add', permission_required('catalogues.add_cataloguecataloguetyperelation')(CatalogueCatalogueTypeRelationCreateView.as_view()),
       name="add_cataloguecataloguetyperelation"),
    path(r'cataloguecataloguetyperelations/edit/<uuid:pk>',
       permission_required('catalogues.change_cataloguecataloguetyperelation')(CatalogueCatalogueTypeRelationUpdateView.as_view()),
       name="change_cataloguecataloguetyperelation"),
    path(r'cataloguecataloguetyperelations/delete/<uuid:pk>',
       permission_required('catalogues.delete_cataloguecataloguetyperelation')(CatalogueCatalogueTypeRelationDeleteView.as_view()),
       name="delete_cataloguecataloguetyperelation"),


    # Collection urls
    path('collections/', permission_required('global.view_all')(CollectionTableView.as_view()), name='collections'),
    path(r'collections/<uuid:pk>', permission_required('global.view_all')(CollectionDetailView.as_view()),
       name="collection_detail"),
    path(r'collections/add', permission_required('catalogues.add_collection')(CollectionCreateView.as_view()),
       name="add_collection"),
    path(r'collections/edit/<uuid:pk>',
       permission_required('catalogues.change_collection')(CollectionUpdateView.as_view()),
       name="change_collection"),
    path(r'collections/delete/<uuid:pk>',
       permission_required('catalogues.delete_collection')(CollectionDeleteView.as_view()),
       name="delete_collection"),


    # CollectionYear urls
    path('collectionyears/', permission_required('global.view_all')(CollectionYearTableView.as_view()), name='collectionyears'),
    path(r'collectionyears/<uuid:pk>', permission_required('global.view_all')(CollectionYearDetailView.as_view()),
       name="collectionyear_detail"),
    path(r'collectionyears/add', permission_required('catalogues.add_collectionyear')(CollectionYearCreateView.as_view()),
       name="add_collectionyear"),
    path(r'collectionyears/edit/<uuid:pk>',
       permission_required('catalogues.change_collectionyear')(CollectionYearUpdateView.as_view()),
       name="change_collectionyear"),
    path(r'collectionyears/delete/<uuid:pk>',
       permission_required('catalogues.delete_collectionyear')(CollectionYearDeleteView.as_view()),
       name="delete_collectionyear"),


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


    # PersonCatalogueRelation urls
    path('personcataloguerelations/', permission_required('global.view_all')(PersonCatalogueRelationTableView.as_view()), name='personcataloguerelations'),
    path(r'personcataloguerelations/<uuid:pk>', permission_required('global.view_all')(PersonCatalogueRelationDetailView.as_view()),
       name="personcataloguerelation_detail"),
    path(r'personcataloguerelations/add', permission_required('catalogues.add_personcataloguerelation')(PersonCatalogueRelationCreateView.as_view()),
       name="add_personcataloguerelation"),
    path(r'personcataloguerelations/edit/<uuid:pk>',
       permission_required('catalogues.change_personcataloguerelation')(PersonCatalogueRelationUpdateView.as_view()),
       name="change_personcataloguerelation"),
    path(r'personcataloguerelations/delete/<uuid:pk>',
       permission_required('catalogues.delete_personcataloguerelation')(PersonCatalogueRelationDeleteView.as_view()),
       name="delete_personcataloguerelation"),


    # PersonCatalogueRelationRole urls
    path('personcataloguerelationroles/', permission_required('global.view_all')(PersonCatalogueRelationRoleTableView.as_view()), name='personcataloguerelationroles'),
    path(r'personcataloguerelationroles/<uuid:pk>', permission_required('global.view_all')(PersonCatalogueRelationRoleDetailView.as_view()),
       name="personcataloguerelationrole_detail"),
    path(r'personcataloguerelationroles/add', permission_required('catalogues.add_personcataloguerelationrole')(PersonCatalogueRelationRoleCreateView.as_view()),
       name="add_personcataloguerelationrole"),
    path(r'personcataloguerelationroles/edit/<uuid:pk>',
       permission_required('catalogues.change_personcataloguerelationrole')(PersonCatalogueRelationRoleUpdateView.as_view()),
       name="change_personcataloguerelationrole"),
    path(r'personcataloguerelationroles/delete/<uuid:pk>',
       permission_required('catalogues.delete_personcataloguerelationrole')(PersonCatalogueRelationRoleDeleteView.as_view()),
       name="delete_personcataloguerelationrole"),


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


    # CataloguePlaceRelation urls
    path('catalogueplacerelations/', permission_required('global.view_all')(CataloguePlaceRelationTableView.as_view()), name='catalogueplacerelations'),
    path(r'catalogueplacerelations/<uuid:pk>', permission_required('global.view_all')(CataloguePlaceRelationDetailView.as_view()),
         name="catalogueplacerelation_detail"),
    path(r'catalogueplacerelations/add', permission_required('catalogues.add_catalogueplacerelation')(CataloguePlaceRelationCreateView.as_view()),
         name="add_catalogueplacerelation"),
    path(r'catalogueplacerelations/edit/<uuid:pk>',
         permission_required('catalogues.change_catalogueplacerelation')(CataloguePlaceRelationUpdateView.as_view()),
         name="change_catalogueplacerelation"),
    path(r'catalogueplacerelations/delete/<uuid:pk>',
         permission_required('catalogues.delete_catalogueplacerelation')(CataloguePlaceRelationDeleteView.as_view()),
         name="delete_catalogueplacerelation"),


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


    # CataloguePlaceRelationType urls
    path('catalogueplacerelationtypes/', permission_required('global.view_all')(CataloguePlaceRelationTypeTableView.as_view()), name='catalogueplacerelationtypes'),
    path(r'catalogueplacerelationtypes/<uuid:pk>', permission_required('global.view_all')(CataloguePlaceRelationTypeDetailView.as_view()),
       name="catalogueplacerelationtype_detail"),
    path(r'catalogueplacerelationtypes/add', permission_required('catalogues.add_catalogueplacerelationtype')(CataloguePlaceRelationTypeCreateView.as_view()),
       name="add_catalogueplacerelationtype"),
    path(r'catalogueplacerelationtypes/edit/<uuid:pk>',
       permission_required('catalogues.change_catalogueplacerelationtype')(CataloguePlaceRelationTypeUpdateView.as_view()),
       name="change_catalogueplacerelationtype"),
    path(r'catalogueplacerelationtypes/delete/<uuid:pk>',
       permission_required('catalogues.delete_catalogueplacerelationtype')(CataloguePlaceRelationTypeDeleteView.as_view()),
       name="delete_catalogueplacerelationtype"),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)