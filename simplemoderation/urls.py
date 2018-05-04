from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required, permission_required
from .views import *

urlpatterns = [
    path(r'', RedirectView.as_view(url='moderations/')),

    # Moderation urls
    path('moderations/', login_required(ModerationTableView.as_view()), name='moderations'),
    path(r'moderations/edit/<int:pk>',
         permission_required('simplemoderation.change_moderation')(ModerationUpdateView.as_view()),
         name="change_moderation"),
    ]