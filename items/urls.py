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
         name="change_item"),


    # Language urls
    path('languages/', login_required(LanguageTableView.as_view()), name='languages'),
    path(r'languages/<uuid:pk>', login_required(LanguageDetailView.as_view()), name="language_detail"),
    path(r'languages/add', permission_required('items.add_language')(LanguageCreateView.as_view()),
         name="add_language"),
    path(r'languages/edit/<uuid:pk>', permission_required('items.change_language')(LanguageUpdateView.as_view()),
         name="change_language"),
    path(r'languages/delete/<uuid:pk>', permission_required('items.delete_language')(LanguageDeleteView.as_view()),
         name="delete_language"),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
