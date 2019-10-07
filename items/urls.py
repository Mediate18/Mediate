from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required, permission_required
from .views.views import *

urlpatterns = [
    path(r'', RedirectView.as_view(url='items/')),

    # BookFormat urls
    path('bookformats/', permission_required('global.view_all')(BookFormatTableView.as_view()), name='bookformats'),
    path(r'bookformats/<uuid:pk>', permission_required('global.view_all')(BookFormatDetailView.as_view()),
       name="bookformat_detail"),
    path(r'bookformats/add', permission_required('items.add_bookformat')(BookFormatCreateView.as_view()),
       name="add_bookformat"),
    path(r'bookformats/edit/<uuid:pk>',
       permission_required('items.change_bookformat')(BookFormatUpdateView.as_view()),
       name="change_bookformat"),
    path(r'bookformats/delete/<uuid:pk>',
       permission_required('items.delete_bookformat')(BookFormatDeleteView.as_view()),
       name="delete_bookformat"),

    # Item urls
    path('items/', permission_required('global.view_all')(ItemTableView.as_view()), name='items'),
    path(r'items/<uuid:pk>', permission_required('global.view_all')(ItemDetailView.as_view()), name="item_detail"),
    path(r'items/add', permission_required('items.add_item')(ItemAndEditionCreateView.as_view()),
       name="add_item"),
    path(r'items/edit/<uuid:pk>', permission_required('items.change_item')(ItemAndEditionUpdateView.as_view()),
       name="change_item"),
    path(r'items/delete/<uuid:pk>', permission_required('items.delete_item')(ItemDeleteView.as_view()),
       name="delete_item"),
    path('items/map', permission_required('global.view_all')(ItemLocationMapView.as_view()), name='itemsmap'),
    path('items/set_bookformat', permission_required('items.change_item')(set_bookformat_for_items),
         name='set_bookformat'),

    # Tagged Item urls
    path('taggeditems/', login_required(TaggedItemTableView.as_view()), name='taggeditems'),

    # ItemAuthor urls
    path('itemauthors/', permission_required('global.view_all')(ItemAuthorTableView.as_view()), name='itemauthors'),
    path(r'itemauthors/<uuid:pk>', permission_required('global.view_all')(ItemAuthorDetailView.as_view()),
       name="itemauthor_detail"),
    path(r'itemauthors/add', permission_required('items.add_itemauthor')(ItemAuthorCreateView.as_view()),
       name="add_itemauthor"),
    path(r'itemauthors/edit/<uuid:pk>',
       permission_required('items.change_itemauthor')(ItemAuthorUpdateView.as_view()),
       name="change_itemauthor"),
    path(r'itemauthors/delete/<uuid:pk>',
       permission_required('items.delete_itemauthor')(ItemAuthorDeleteView.as_view()),
       name="delete_itemauthor"),

    # ItemItemTypeRelation urls
    path('itemitemtyperelations/', permission_required('global.view_all')(ItemItemTypeRelationTableView.as_view()),
       name='itemitemtyperelations'),
    path(r'itemitemtyperelations/<uuid:pk>', permission_required('global.view_all')(ItemItemTypeRelationDetailView.as_view()),
       name="itemitemtyperelation_detail"),
    path(r'itemitemtyperelations/add',
       permission_required('items.add_itemitemtyperelation')(ItemItemTypeRelationCreateView.as_view()),
       name="add_itemitemtyperelation"),
    path(r'itemitemtyperelations/edit/<uuid:pk>',
       permission_required('items.change_itemitemtyperelation')(
           ItemItemTypeRelationUpdateView.as_view()),
       name="change_itemitemtyperelation"),
    path(r'itemitemtyperelations/delete/<uuid:pk>',
       permission_required('items.delete_itemitemtyperelation')(
           ItemItemTypeRelationDeleteView.as_view()),
       name="delete_itemitemtyperelation"),

    # ItemLanguageRelation urls
    path('itemlanguagerelations/', permission_required('global.view_all')(ItemLanguageRelationTableView.as_view()),
       name='itemlanguagerelations'),
    path(r'itemlanguagerelations/<uuid:pk>', permission_required('global.view_all')(ItemLanguageRelationDetailView.as_view()),
       name="itemlanguagerelation_detail"),
    path(r'itemlanguagerelations/add',
       permission_required('items.add_itemlanguagerelation')(ItemLanguageRelationCreateView.as_view()),
       name="add_itemlanguagerelation"),
    path(r'itemlanguagerelations/edit/<uuid:pk>',
       permission_required('items.change_itemlanguagerelation')(
           ItemLanguageRelationUpdateView.as_view()),
       name="change_itemlanguagerelation"),
    path(r'itemlanguagerelations/delete/<uuid:pk>',
       permission_required('items.delete_itemlanguagerelation')(
           ItemLanguageRelationDeleteView.as_view()),
       name="delete_itemlanguagerelation"),

    # ItemMaterialDetailsRelation urls
    path('itemmaterialdetailsrelations/', permission_required('global.view_all')(ItemMaterialDetailsRelationTableView.as_view()),
       name='itemmaterialdetailsrelations'),
    path(r'itemmaterialdetailsrelations/<uuid:pk>',
       permission_required('global.view_all')(ItemMaterialDetailsRelationDetailView.as_view()),
       name="itemmaterialdetailsrelation_detail"),
    path(r'itemmaterialdetailsrelations/add',
       permission_required('items.add_itemmaterialdetailsrelation')(
           ItemMaterialDetailsRelationCreateView.as_view()),
       name="add_itemmaterialdetailsrelation"),
    path(r'itemmaterialdetailsrelations/edit/<uuid:pk>',
       permission_required('items.change_itemmaterialdetailsrelation')(
           ItemMaterialDetailsRelationUpdateView.as_view()),
       name="change_itemmaterialdetailsrelation"),
    path(r'itemmaterialdetailsrelations/delete/<uuid:pk>',
       permission_required('items.delete_itemmaterialdetailsrelation')(
           ItemMaterialDetailsRelationDeleteView.as_view()),
       name="delete_itemmaterialdetailsrelation"),

    # ItemType urls
    path('itemtypes/', permission_required('global.view_all')(ItemTypeTableView.as_view()), name='itemtypes'),
    path(r'itemtypes/<uuid:pk>', permission_required('global.view_all')(ItemTypeDetailView.as_view()), name="itemtype_detail"),
    path(r'itemtypes/add', permission_required('items.add_itemtype')(ItemTypeCreateView.as_view()),
       name="add_itemtype"),
    path(r'itemtypes/edit/<uuid:pk>',
       permission_required('items.change_itemtype')(ItemTypeUpdateView.as_view()),
       name="change_itemtype"),
    path(r'itemtypes/delete/<uuid:pk>',
       permission_required('items.delete_itemtype')(ItemTypeDeleteView.as_view()),
       name="delete_itemtype"),

    # ItemWorkRelation urls
    path('itemworkrelations/', permission_required('global.view_all')(ItemWorkRelationTableView.as_view()),
       name='itemworkrelations'),
    path(r'itemworkrelations/<uuid:pk>', permission_required('global.view_all')(ItemWorkRelationDetailView.as_view()),
       name="itemworkrelation_detail"),
    path(r'itemworkrelations/add',
       permission_required('items.add_itemworkrelation')(ItemWorkRelationCreateView.as_view()),
       name="add_itemworkrelation"),
    path(r'itemworkrelations/edit/<uuid:pk>',
       permission_required('items.change_itemworkrelation')(ItemWorkRelationUpdateView.as_view()),
       name="change_itemworkrelation"),
    path(r'itemworkrelations/delete/<uuid:pk>',
       permission_required('items.delete_itemworkrelation')(ItemWorkRelationDeleteView.as_view()),
       name="delete_itemworkrelation"),

    # Add works to item
    path(r'itemworkrelations/addworkstoitem/<uuid:pk>',
         permission_required('items.add_itemworkrelation')(ItemWorkRelationAddView.as_view()),
         name="add_workstoitem"),

    # WorkAndVIAF API
    path(r'workandviaf_suggest', WorkAndVIAFSuggest.as_view(), name='workandviaf_suggest'),
    path(r'person_viaf_suggest', PersonVIAFSuggest.as_view(), name='person_viaf_suggest'),
    path(r'work_viaf_suggest', WorkVIAFSuggest.as_view(), name='work_viaf_suggest'),
    path(r'viaf_suggest', VIAFSuggest.as_view(), name='viaf_suggest'),

    # Language urls
    path('languages/', permission_required('global.view_all')(LanguageTableView.as_view()), name='languages'),
    path(r'languages/<uuid:pk>', permission_required('global.view_all')(LanguageDetailView.as_view()), name="language_detail"),
    path(r'languages/add', permission_required('items.add_language')(LanguageCreateView.as_view()),
       name="add_language"),
    path(r'languages/edit/<uuid:pk>',
       permission_required('items.change_language')(LanguageUpdateView.as_view()),
       name="change_language"),
    path(r'languages/delete/<uuid:pk>',
       permission_required('items.delete_language')(LanguageDeleteView.as_view()),
       name="delete_language"),

    # MaterialDetails urls
    path('materialdetails/', permission_required('global.view_all')(MaterialDetailsTableView.as_view()),
       name='materialdetails'),
    path(r'materialdetails/<uuid:pk>', permission_required('global.view_all')(MaterialDetailsDetailView.as_view()),
       name="materialdetails_detail"),
    path(r'materialdetails/add',
       permission_required('items.add_materialdetails')(MaterialDetailsCreateView.as_view()),
       name="add_materialdetails"),
    path(r'materialdetails/edit/<uuid:pk>',
       permission_required('items.change_materialdetails')(MaterialDetailsUpdateView.as_view()),
       name="change_materialdetails"),
    path(r'materialdetails/delete/<uuid:pk>',
       permission_required('items.delete_materialdetails')(MaterialDetailsDeleteView.as_view()),
       name="delete_materialdetails"),

    # PersonItemRelation urls
    path('personitemrelations/', permission_required('global.view_all')(PersonItemRelationTableView.as_view()),
       name='personitemrelations'),
    path(r'personitemrelations/<uuid:pk>', permission_required('global.view_all')(PersonItemRelationDetailView.as_view()),
       name="personitemrelation_detail"),
    path(r'personitemrelations/add',
       permission_required('items.add_personitemrelation')(PersonItemRelationCreateView.as_view()),
       name="add_personitemrelation"),
    path(r'personitemrelations/edit/<uuid:pk>',
       permission_required('items.change_personitemrelation')(PersonItemRelationUpdateView.as_view()),
       name="change_personitemrelation"),
    path(r'personitemrelations/delete/<uuid:pk>',
       permission_required('items.delete_personitemrelation')(PersonItemRelationDeleteView.as_view()),
       name="delete_personitemrelation"),

    # Add persons (plural) to item (singular)
    path(r'personitemrelations/addpersonstoitem/<uuid:pk>',
         permission_required('items.add_personitemrelation')(PersonItemRelationAddView.as_view()),
         name="add_personstoitem"),

    # Add person (singular) to items (plural)
    path(r'personitemrelations/addpersontoitems/',
         permission_required('items.add_personitemrelation')(add_person_to_items),
         name="add_persontoitems"),

    # PersonItemRelationRole urls
    path('personitemrelationroles/', permission_required('global.view_all')(PersonItemRelationRoleTableView.as_view()),
       name='personitemrelationroles'),
    path(r'personitemrelationroles/<uuid:pk>', permission_required('global.view_all')(PersonItemRelationRoleDetailView.as_view()),
       name="personitemrelationrole_detail"),
    path(r'personitemrelationroles/add', permission_required('items.add_personitemrelationrole')(
      PersonItemRelationRoleCreateView.as_view()),
       name="add_personitemrelationrole"),
    path(r'personitemrelationroles/edit/<uuid:pk>',
       permission_required('items.change_personitemrelationrole')(
           PersonItemRelationRoleUpdateView.as_view()),
       name="change_personitemrelationrole"),
    path(r'personitemrelationroles/delete/<uuid:pk>',
       permission_required('items.delete_personitemrelationrole')(
           PersonItemRelationRoleDeleteView.as_view()),
       name="delete_personitemrelationrole"),

    # Edition urls
    path('editions/', permission_required('global.view_all')(EditionTableView.as_view()), name='editions'),
    path(r'editions/<uuid:pk>', permission_required('global.view_all')(EditionDetailView.as_view()),
         name="edition_detail"),
    path(r'editions/add',
         permission_required('items.add_edition')(ItemAndEditionCreateView.as_view()),
         name="add_edition"),
    path(r'editions/edit/<uuid:pk>',
         permission_required('items.change_edition')(EditionUpdateView.as_view()),
         name="change_edition"),
    path(r'editions/delete/<uuid:pk>',
         permission_required('items.delete_edition')(EditionDeleteView.as_view()),
         name="delete_edition"),
    path(r'editions/setplace/', permission_required('global.view_all')(set_publication_place_for_items),
         name="set_editionplace"),

    # Publisher urls
    path('publishers/', permission_required('global.view_all')(PublisherTableView.as_view()), name='publishers'),
    path(r'publishers/<uuid:pk>', permission_required('global.view_all')(PublisherDetailView.as_view()), name="publisher_detail"),
    path(r'publishers/add', permission_required('items.add_publisher')(PublisherCreateView.as_view()),
       name="add_publisher"),
    path(r'publishers/edit/<uuid:pk>',
       permission_required('items.change_publisher')(PublisherUpdateView.as_view()),
       name="change_publisher"),
    path(r'publishers/delete/<uuid:pk>',
       permission_required('items.delete_publisher')(PublisherDeleteView.as_view()),
       name="delete_publisher"),

    # Subject urls
    path('subjects/', permission_required('global.view_all')(SubjectTableView.as_view()), name='subjects'),
    path(r'subjects/<uuid:pk>', permission_required('global.view_all')(SubjectDetailView.as_view()), name="subject_detail"),
    path(r'subjects/add', permission_required('items.add_subject')(SubjectCreateView.as_view()),
       name="add_subject"),
    path(r'subjects/edit/<uuid:pk>',
       permission_required('items.change_subject')(SubjectUpdateView.as_view()),
       name="change_subject"),
    path(r'subjects/delete/<uuid:pk>',
       permission_required('items.delete_subject')(SubjectDeleteView.as_view()),
       name="delete_subject"),

    # Work urls
    path('works/', permission_required('global.view_all')(WorkTableView.as_view()), name='works'),
    path(r'works/<uuid:pk>', permission_required('global.view_all')(WorkDetailView.as_view()), name="work_detail"),
    path(r'works/add', permission_required('items.add_work')(WorkCreateView.as_view()),
       name="add_work"),
    path(r'works/edit/<uuid:pk>', permission_required('items.change_work')(WorkUpdateView.as_view()),
       name="change_work"),
    path(r'works/delete/<uuid:pk>', permission_required('items.delete_work')(WorkDeleteView.as_view()),
       name="delete_work"),

    # WorkAuthor urls
    path('workauthors/', permission_required('global.view_all')(WorkAuthorTableView.as_view()), name='workauthors'),
    path(r'workauthors/<uuid:pk>', permission_required('global.view_all')(WorkAuthorDetailView.as_view()),
       name="workauthor_detail"),
    path(r'workauthors/add', permission_required('items.add_workauthor')(WorkAuthorCreateView.as_view()),
       name="add_workauthor"),
    path(r'workauthors/edit/<uuid:pk>',
       permission_required('items.change_workauthor')(WorkAuthorUpdateView.as_view()),
       name="change_workauthor"),
    path(r'workauthors/delete/<uuid:pk>',
       permission_required('items.delete_workauthor')(WorkAuthorDeleteView.as_view()),
       name="delete_workauthor"),

    # WorkSubject urls
    path('worksubjects/', permission_required('global.view_all')(WorkSubjectTableView.as_view()), name='worksubjects'),
    path(r'worksubjects/<uuid:pk>', permission_required('global.view_all')(WorkSubjectDetailView.as_view()),
       name="worksubject_detail"),
    path(r'worksubjects/add',
       permission_required('items.add_worksubject')(WorkSubjectCreateView.as_view()),
       name="add_worksubject"),
    path(r'worksubjects/edit/<uuid:pk>',
       permission_required('items.change_worksubject')(WorkSubjectUpdateView.as_view()),
       name="change_worksubject"),
    path(r'worksubjects/delete/<uuid:pk>',
       permission_required('items.delete_worksubject')(WorkSubjectDeleteView.as_view()),
       name="delete_worksubject"),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
