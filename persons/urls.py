from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required, permission_required
from .views.views import *

urlpatterns = [
    path(r'', RedirectView.as_view(url='persons/')),

    # Person urls
    path('persons/', login_required(PersonTableView.as_view()), name='persons'),
    path(r'persons/<uuid:pk>', login_required(PersonDetailView.as_view()),
         name="person_detail"),
    path(r'persons/add', permission_required('persons.add_person')(PersonCreateView.as_view()),
         name="add_person"),
    path(r'persons/edit/<uuid:pk>',
         permission_required('persons.change_person')(PersonUpdateView.as_view()),
         name="change_person"),
    path(r'persons/delete/<uuid:pk>',
         permission_required('catalogue.delete_person')(PersonDeleteView.as_view()),
         name="delete_person"),

    # PersonPersonRelation urls
    path('personpersonrelations/', login_required(PersonPersonRelationTableView.as_view()),
         name='personpersonrelations'),
    path(r'personpersonrelations/<uuid:pk>', login_required(PersonPersonRelationDetailView.as_view()),
         name="personpersonrelation_detail"),
    path(r'personpersonrelations/add',
         permission_required('persons.add_personpersonrelation')(PersonPersonRelationCreateView.as_view()),
         name="add_personpersonrelation"),
    path(r'personpersonrelations/edit/<uuid:pk>',
         permission_required('persons.change_personpersonrelation')(PersonPersonRelationUpdateView.as_view()),
         name="change_personpersonrelation"),
    path(r'personpersonrelations/delete/<uuid:pk>',
         permission_required('catalogue.delete_personpersonrelation')(PersonPersonRelationDeleteView.as_view()),
         name="delete_personpersonrelation"),

    # PersonPersonRelationType urls
    path('personpersonrelationtypes/', login_required(PersonPersonRelationTypeTableView.as_view()),
         name='personpersonrelationtypes'),
    path(r'personpersonrelationtypes/<uuid:pk>', login_required(PersonPersonRelationTypeDetailView.as_view()),
         name="personpersonrelationtype_detail"),
    path(r'personpersonrelationtypes/add',
         permission_required('persons.add_personpersonrelationtype')(PersonPersonRelationTypeCreateView.as_view()),
         name="add_personpersonrelationtype"),
    path(r'personpersonrelationtypes/edit/<uuid:pk>',
         permission_required('persons.change_personpersonrelationtype')(
             PersonPersonRelationTypeUpdateView.as_view()),
         name="change_personpersonrelationtype"),
    path(r'personpersonrelationtypes/delete/<uuid:pk>',
         permission_required('catalogue.delete_personpersonrelationtype')(PersonPersonRelationTypeDeleteView.as_view()),
         name="delete_personpersonrelationtype"),

    # PersonProfession urls
    path('personprofessions/', login_required(PersonProfessionTableView.as_view()), name='personprofessions'),
    path(r'personprofessions/<uuid:pk>', login_required(PersonProfessionDetailView.as_view()),
         name="personprofession_detail"),
    path(r'personprofessions/add',
         permission_required('persons.add_personprofession')(PersonProfessionCreateView.as_view()),
         name="add_personprofession"),
    path(r'personprofessions/edit/<uuid:pk>',
         permission_required('persons.change_personprofession')(PersonProfessionUpdateView.as_view()),
         name="change_personprofession"),
    path(r'personprofessions/delete/<uuid:pk>',
         permission_required('catalogue.delete_personprofession')(PersonProfessionDeleteView.as_view()),
         name="delete_personprofession"),

    # Place urls
    path('places/', login_required(PlaceTableView.as_view()), name='places'),
    path(r'places/<uuid:pk>', login_required(PlaceDetailView.as_view()),
         name="place_detail"),
    path(r'places/add', permission_required('persons.add_place')(PlaceCreateView.as_view()),
         name="add_place"),
    path(r'places/edit/<uuid:pk>',
         permission_required('persons.change_place')(PlaceUpdateView.as_view()),
         name="change_place"),
    path(r'places/delete/<uuid:pk>',
         permission_required('catalogue.delete_place')(PlaceDeleteView.as_view()),
         name="delete_place"),

    # Profession urls
    path('professions/', login_required(ProfessionTableView.as_view()), name='professions'),
    path(r'professions/<uuid:pk>', login_required(ProfessionDetailView.as_view()),
         name="profession_detail"),
    path(r'professions/add', permission_required('persons.add_profession')(ProfessionCreateView.as_view()),
         name="add_profession"),
    path(r'professions/edit/<uuid:pk>',
         permission_required('persons.change_profession')(ProfessionUpdateView.as_view()),
         name="change_profession"),
    path(r'professions/delete/<uuid:pk>',
         permission_required('catalogue.delete_profession')(ProfessionDeleteView.as_view()),
         name="delete_profession"),

    # Religion urls
    path('religions/', login_required(ReligionTableView.as_view()), name='religions'),
    path(r'religions/<uuid:pk>', login_required(ReligionDetailView.as_view()),
         name="religion_detail"),
    path(r'religions/add', permission_required('persons.add_religion')(ReligionCreateView.as_view()),
         name="add_religion"),
    path(r'religions/edit/<uuid:pk>',
         permission_required('persons.change_religion')(ReligionUpdateView.as_view()),
         name="change_religion"),
    path(r'religions/delete/<uuid:pk>',
         permission_required('catalogue.delete_religion')(ReligionDeleteView.as_view()),
         name="delete_religion"),

    # ReligiousAffiliation urls
    path('religiousaffiliations/', login_required(ReligiousAffiliationTableView.as_view()),
         name='religiousaffiliations'),
    path(r'religiousaffiliations/<uuid:pk>', login_required(ReligiousAffiliationDetailView.as_view()),
         name="religiousaffiliation_detail"),
    path(r'religiousaffiliations/add',
         permission_required('persons.add_religiousaffiliation')(ReligiousAffiliationCreateView.as_view()),
         name="add_religiousaffiliation"),
    path(r'religiousaffiliations/edit/<uuid:pk>',
         permission_required('persons.change_religiousaffiliation')(ReligiousAffiliationUpdateView.as_view()),
         name="change_religiousaffiliation"),
    path(r'religiousaffiliations/delete/<uuid:pk>',
         permission_required('catalogue.delete_religiousaffiliation')(ReligiousAffiliationDeleteView.as_view()),
         name="delete_religiousaffiliation"),

    # Residence urls
    path('residences/', login_required(ResidenceTableView.as_view()), name='residences'),
    path(r'residences/<uuid:pk>', login_required(ResidenceDetailView.as_view()),
         name="residence_detail"),
    path(r'residences/add', permission_required('persons.add_residence')(ResidenceCreateView.as_view()),
         name="add_residence"),
    path(r'residences/edit/<uuid:pk>',
         permission_required('persons.change_residence')(ResidenceUpdateView.as_view()),
         name="change_residence"),
    path(r'residences/delete/<uuid:pk>',
         permission_required('catalogue.delete_residence')(ResidenceDeleteView.as_view()),
         name="delete_residence"),

    # Cerl API
    path(r'cerl_suggest', CerlSuggest.as_view(), name='cerl_suggest'),
    path(r'placeandcerl_suggest', PlaceAndCerlSuggest.as_view(), name='placeandcerl_suggest'),
]