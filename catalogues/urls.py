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

from django.conf.urls import url, include
from django.views.generic import RedirectView
from rest_framework import routers
from items import views
import items.urls

from django.contrib import admin
from moderation.helpers import auto_discover
admin.autodiscover()
auto_discover()

router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

router.register(r'bindingmaterialdetails', views.BindingMaterialDetailsViewSet)
router.register(r'bindingmaterialdetailsequivalents', views.BindingMaterialDetailsEquivalentViewSet)
router.register(r'bookformats', views.BookFormatViewSet)
router.register(r'bookformatequivalents', views.BookFormatEquivalentViewSet)
router.register(r'items', views.ItemViewSet)
router.register(r'catalogues', views.CatalogueViewSet)
router.register(r'catalogueentries', views.CatalogueEntryViewSet)
router.register(r'cataloguetypes', views.CatalogueTypeViewSet)
router.register(r'languages', views.LanguageViewSet)
router.register(r'persons', views.PersonViewSet)
router.register(r'personitemrelations', views.PersonItemRelationViewSet)
router.register(r'personitemrelationroles', views.PersonItemRelationRoleViewSet)
router.register(r'personcataloguerelations', views.PersonCatalogueRelationViewSet)
router.register(r'personcataloguerelationroles', views.PersonCatalogueRelationRoleViewSet)
router.register(r'places', views.PlaceViewSet)
router.register(r'placeequivalents', views.PlaceEquivalentViewSet)
router.register(r'placetypes', views.PlaceTypeViewSet)
router.register(r'publishers', views.PublisherViewSet)
router.register(r'publisherequivalents', views.PublisherEquivalentViewSet)
router.register(r'titleworks', views.TitleWorkViewSet)


urlpatterns = [
    path(r'', RedirectView.as_view(url='items/')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path(r'items/', include(items.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
