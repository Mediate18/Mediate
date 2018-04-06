from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required, permission_required
from .views.views import *

urlpatterns = [
    path(r'', RedirectView.as_view(url='items/')),
    path(r'items/', login_required(ItemTableView.as_view()), name="items"),
    path(r'items/<int:pk>', RedirectView.as_view(url=reverse_lazy('items')), name="item_detail"),  # TODO
    path(r'lots/', login_required(LotListView.as_view()), name="lots"),
    path(r'lots/<int:pk>', RedirectView.as_view(url=reverse_lazy('lots')), name="lot_detail"),  # TODO

    # Edit forms
    path(r'items/add', permission_required('items.add_item')(ItemCreateView.as_view()),
         name="add_item"),
    path(r'items/edit/<int:pk>', permission_required('items.change_item')(ItemUpdateView.as_view()),
         name="add_item"),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
