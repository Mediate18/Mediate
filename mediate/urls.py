"""Catalogues URL Configuration

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

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

from django.conf.urls import url, include
from django.views.generic import RedirectView
from rest_framework import routers

from .views import protected_media

import items.urls
import catalogues.urls
import persons.urls
import transcriptions.urls
from dashboard.views import view_dashboard

from catalogues.views.api_views import *
from items.views.api_views import *
from persons.views.api_views import *
from transcriptions.views.api_views import *

from django.contrib import admin
admin.autodiscover()

router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

# Catalogues app
router.register(r'collection', CollectionViewSet)
router.register(r'collectionyear', CollectionYearViewSet)
router.register(r'cataloguetype', CatalogueTypeViewSet)
router.register(r'library', LibraryViewSet)
router.register(r'catalogue', CatalogueViewSet)
router.register(r'cataloguecataloguetyperelation', CatalogueCatalogueTypeRelationViewSet)
router.register(r'catalogueheldby', CatalogueHeldByViewSet)
router.register(r'lot', LotViewSet)
router.register(r'personcollectionrelation', PersonCollectionRelationViewSet)
router.register(r'personcataloguerelationrole', PersonCatalogueRelationRoleViewSet)
router.register(r'personcataloguerelation', PersonCatalogueRelationViewSet)
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
router.register(r'manifestation', ManifestationViewSet)
router.register(r'publisher', PublisherViewSet)
router.register(r'personitemrelationrole', PersonItemRelationRoleViewSet)
router.register(r'personitemrelation', PersonItemRelationViewSet)

# Persons app
router.register(r'place', PlaceViewSet)
router.register(r'religion', ReligionViewSet)
router.register(r'person', PersonViewSet)
router.register(r'religiousaffiliation', ReligiousAffiliationViewSet)
router.register(r'residence', ResidenceViewSet)
router.register(r'profession', ProfessionViewSet)
router.register(r'personprofession', PersonProfessionViewSet)
router.register(r'personpersonrelationtype', PersonPersonRelationTypeViewSet)
router.register(r'personpersonrelation', PersonPersonRelationViewSet)
router.register(r'languages', items.views.LanguageViewSet)

# Transcription app
router.register(r'sourcematerial', SourceMaterialViewSet)
router.register(r'transcription', TranscriptionViewSet)
router.register(r'documentscan', DocumentScanViewSet)


urlpatterns = [
    path(r'', RedirectView.as_view(url='dashboard/'), name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path(r'items/', include(items.urls)),
    path(r'catalogues/', include(catalogues.urls)),
    path(r'persons/', include(persons.urls)),
    path(r'transcriptions/', include(transcriptions.urls)),
    path(r'dashboard/', login_required(view_dashboard), name='dashboard'),
    path(r'moderation/', include('simplemoderation.urls')),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^select2/', include('django_select2.urls')),
    url(r'^viaf/', include(('viapy.urls', 'viapy'), namespace='viaf'), name='viaf'),
    url(r'protected_media/(?P<filename>.*)$', protected_media, name='protected_media'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
