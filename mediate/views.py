from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext_lazy as _
import os
import mimetypes
import json
from django.conf import settings
from django.http import Http404, HttpResponse
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ObjectDoesNotExist

from mediate.forms import SelectDatasetForm
from catalogues.models import Dataset
from catalogues.tools import get_dataset_for_anonymoususer

# When a user logs in, he/she should choose a Dataset.
# To make this happen, set dataset in session to None after login.
def login_handler(sender, user, request, **kwargs):
    request.session['dataset'] = None

user_logged_in.connect(login_handler)


@permission_required('global.view_all')
def protected_media(request, filename):
    """
    View to send file via X-Sendfile
    :param request: the HTTP request
    :param filename: the filename, extracted from the url
    :return: a HttpResponse object
    """
    # Construct full path and base name
    full_path = os.path.join(settings.MEDIA_ROOT, filename)
    base_name = os.path.basename(filename)

    # Check whether the file exist
    if not os.path.exists(full_path):
        raise Http404(_("The requested file does not exist"))

    # Let Django serve it if the XSENDFILE setting is false
    if not settings.XSENDFILE:
        from django.views.static import serve
        return serve(request, full_path, document_root='/')

    # Determine the mime type
    (mime_type, encoding) = mimetypes.guess_type(full_path)

    # Construct the response
    response = HttpResponse(content_type=mime_type)
    response['Content-Disposition'] = 'inline;filename='+base_name
    response['X-Sendfile'] = full_path

    return response


class GenericDetailView(DetailView):
    """
    A DetailView that uses a generic detail template and lists object field-value pairs
    given by the class field 'object_fields'.
    """
    template_name = 'generic_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        obj = self.get_object()
        context['object_name'] = self.model.__name__

        if hasattr(self, 'object_fields'):
            context['object_dict'] = dict([
                (field.replace('_', ' '), getattr(obj, field) if getattr(obj, field) is not None else '-')
                for field in self.object_fields
            ])

        context['edit_url'] = reverse_lazy('change_' + self.model.__name__.lower(), args=[obj.pk])
        return context


def select_dataset(request):
    """
    Select a Dataset for the current session
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = SelectDatasetForm(request.POST, request=request)
        if form.is_valid():
            datasets = form.cleaned_data['datasets']

            request.session['datasets'] = [
                {'uuid': str(dataset.uuid), 'name': dataset.name}
                for dataset in datasets if request.user.has_perm('collections.change_dataset', dataset)
            ]
            return redirect('dashboard')
    else:
        form = SelectDatasetForm(request=request)

    return render(request, 'generic_form.html', {'form': form})
