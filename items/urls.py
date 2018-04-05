from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required, permission_required
from .views.views import *

urlpatterns = [
    path(r'', RedirectView.as_view(url='items/')),
    path(r'lots/', login_required(LotListView.as_view()), name="lots"),
    path(r'items/', login_required(ItemListView.as_view()), name="items"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
