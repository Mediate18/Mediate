"""Collections URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

from django.conf.urls import include
from django.views.generic import RedirectView, TemplateView
from rest_framework import routers

from .views import protected_media

import items.urls
import catalogues.urls
import persons.urls
import transcriptions.urls
from dashboard.views import view_dashboard, view_totals, get_dashboard_stats

from mediate. views import select_dataset
from catalogues.views.api_views import *
from items.views.api_views import *
from persons.views.api_views import *
from transcriptions.views.api_views import *

from django_registration.backends.activation.views import RegistrationView
from registration.forms import CustomRegistrationForm

from django.contrib import admin
admin.autodiscover()

router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

# Collections app
router.register(r'dataset', DatasetViewSet)
router.register(r'catalogue', CatalogueViewSet)
router.register(r'catalogueyear', CatalogueYearViewSet)
router.register(r'collectiontype', CollectionTypeViewSet)
router.register(r'library', LibraryViewSet)
router.register(r'collection', CollectionViewSet)
router.register(r'collectioncollectiontyperelation', CollectionCollectionTypeRelationViewSet)
router.register(r'collectionheldby', CollectionHeldByViewSet)
router.register(r'lot', LotViewSet)
router.register(r'personcataloguerelation', PersonCatalogueRelationViewSet)
router.register(r'personcollectionrelationrole', PersonCollectionRelationRoleViewSet)
router.register(r'personcollectionrelation', PersonCollectionRelationViewSet)
router.register(r'parisiancategory', ParisianCategoryViewSet)
router.register(r'category', CategoryViewSet)

# Items app
router.register(r'language', LanguageViewSet)
router.register(r'bookformat', BookFormatViewSet)
router.register(r'materialdetails', MaterialDetailsViewSet)
router.register(r'subject', SubjectViewSet)
router.register(r'work', WorkViewSet)
router.register(r'worksubject', WorkSubjectViewSet)
router.register(r'workauthor', WorkAuthorViewSet)
router.register(r'item', ItemViewSet)
router.register(r'itemtype', ItemTypeViewSet)
router.register(r'itemitemtyperelation', ItemItemTypeRelationViewSet)
router.register(r'itemauthor', ItemAuthorViewSet)
router.register(r'itemlanguagerelation', ItemLanguageRelationViewSet)
router.register(r'itemworkrelation', ItemWorkRelationViewSet)
router.register(r'itemmaterialdetailsrelation', ItemMaterialDetailsRelationViewSet)
router.register(r'edition', EditionViewSet)
router.register(r'publisher', PublisherViewSet)
router.register(r'personitemrelationrole', PersonItemRelationRoleViewSet)
router.register(r'personitemrelation', PersonItemRelationViewSet)

# Persons app
router.register(r'country', CountryViewSet)
router.register(r'place', PlaceViewSet)
router.register(r'religion', ReligionViewSet)
router.register(r'person', PersonViewSet)
router.register(r'religiousaffiliation', ReligiousAffiliationViewSet)
router.register(r'residence', ResidenceViewSet)
router.register(r'profession', ProfessionViewSet)
router.register(r'personprofession', PersonProfessionViewSet)
router.register(r'personpersonrelationtype', PersonPersonRelationTypeViewSet)
router.register(r'personpersonrelation', PersonPersonRelationViewSet)

# Transcription app
router.register(r'sourcematerial', SourceMaterialViewSet)
router.register(r'transcription', TranscriptionViewSet)
router.register(r'documentscan', DocumentScanViewSet)
router.register(r'shelfmark', ShelfmarkViewSet)


urlpatterns = [
    path(r'', RedirectView.as_view(url='dashboard/'), name='home'),
    path('about/', TemplateView.as_view(template_name="about.html"), name='about'),
    path(settings.ADMIN_URL_NAME+'/', admin.site.urls),
    path('accounts/register/', RegistrationView.as_view(form_class=CustomRegistrationForm),
         name="django_registration_register"),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    re_path(r'items/', include(items.urls)),
    path(r'catalogues/', include(catalogues.urls)),
    path(r'persons/', include(persons.urls)),
    path(r'transcriptions/', include(transcriptions.urls)),
    path(r'dashboard/', login_required(view_dashboard), name='dashboard'),
    path(r'dashboard_stats/', login_required(get_dashboard_stats), name='get_dashboard_stats'),
    path(r'totals/', view_totals, name='totals'),
    path(r'dataset/', login_required(select_dataset), name='select_dataset'),
    path(r'moderation/', include('simplemoderation.urls')),
    re_path(r'^api/', include(router.urls)),
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^select2/', include('django_select2.urls')),
    re_path(r'protected_media/(?P<filename>.*)$', protected_media, name='protected_media'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.SILK:
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]