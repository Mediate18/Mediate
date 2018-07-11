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
import items.urls
import catalogues.urls
import persons.urls
import transcriptions.urls
from dashboard.views import view_dashboard

from django.contrib import admin
admin.autodiscover()

router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

router.register(r'materialdetails', items.views.MaterialDetailsViewSet)
router.register(r'bookformats', items.views.BookFormatViewSet)
router.register(r'items', items.views.ItemViewSet)
# router.register(r'catalogues', items.views.CatalogueViewSet)
# router.register(r'lots', items.views.LotViewSet)
# router.register(r'cataloguetypes', items.views.CatalogueTypeViewSet)
router.register(r'languages', items.views.LanguageViewSet)
router.register(r'personitemrelations', items.views.PersonItemRelationViewSet)
router.register(r'personitemrelationroles', items.views.PersonItemRelationRoleViewSet)
# router.register(r'personcataloguerelations', items.views.PersonCatalogueRelationViewSet)
# router.register(r'personcataloguerelationroles', items.views.PersonCatalogueRelationRoleViewSet)
router.register(r'publishers', items.views.PublisherViewSet)
router.register(r'works', items.views.WorkViewSet)


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
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
