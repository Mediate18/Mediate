import re

import requests
from django.contrib.auth.decorators import permission_required
from django.utils.translation import gettext_lazy as _
import os
import mimetypes
import json
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ObjectDoesNotExist
from django_select2.views import AutoResponseView

from mediate.forms import SelectDatasetForm
from catalogues.models import Dataset
from catalogues.tools import get_dataset_for_anonymoususer
from persons.models import Country, Person, Place
from transcriptions.models import DocumentScan
from wikidata.utils import get_nested_object
from wikidata.views import get_wikidata_label_translations, get_option_from_wikidata_property, \
    get_wikidata_label_for_property
from wikidata.wikidata_api import get_wikidata_statements, get_wikidata_label


# When a user logs in, he/she should choose a Dataset.
# To make this happen, set dataset in session to None after login.
def login_handler(sender, user, request, **kwargs):
    request.session['dataset'] = None

user_logged_in.connect(login_handler)


def protected_media(request, filename):
    """
    View to send file via X-Sendfile
    :param request: the HTTP request
    :param filename: the filename, extracted from the url
    :return: a HttpResponse object
    """
    # Check permission
    try:
        dataset = DocumentScan.objects.get(scan=filename).shelf_mark.catalogue_set.first().dataset
    except:
       return HttpResponse(_("We can not determine whether you are authorized to view this scan."), status=500)

    if not request.user.has_perm('catalogues.view_dataset', dataset):
        return HttpResponse(_("You do not have permission to view this scan."), status=401)

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
    response[settings.XSENDFILE_HEADER] = full_path

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
                for dataset in datasets if request.user.has_perm('catalogues.change_dataset', dataset)
            ]
            return redirect('dashboard')
    else:
        form = SelectDatasetForm(request=request)

    return render(request, 'generic_form.html', {'form': form})


class FillFieldsView(AutoResponseView):
    def get(self, request, fill_field_name, *args, **kwargs):
        method = f'get_{fill_field_name}_fillfield_response'
        if hasattr(self, method) and callable(getattr(self, method)):
            return JsonResponse(getattr(self, method)(request))
        return JsonResponse({})

    @staticmethod
    def get_country_wikidata_fillfield_response(request):
        api_id = request.GET.get('api_id', "")
        field_values = get_wikidata_label_translations(api_id, "modern_country")
        return field_values

    @staticmethod
    def get_place_wikidata_fillfield_response(request):
        api_id = request.GET.get('api_id', "")
        field_values = get_wikidata_label_translations(api_id, "name")

        if data := get_wikidata_statements(api_id):
            field_values['modern_country'] = get_option_from_wikidata_property(data, 'P17', Country)
            field_values['latitude'] = round(get_nested_object(data, ('statements', 'P625', 0, 'value', 'content', 'latitude')), 6)
            field_values['longitude'] = round(get_nested_object(data, ('statements', 'P625', 0, 'value', 'content', 'longitude')), 6)

        return field_values

    @staticmethod
    def get_person_wikidata_fillfield_response(request):
        api_id = request.GET.get('api_id', "")
        field_values = {}
        if data := get_wikidata_statements(api_id):
            response, request_failed = get_wikidata_label(api_id)
            field_values['short_name'] = response.json() \
                                            if (not request_failed and response.status_code == requests.codes.ok) \
                                            else ''
            field_values['first_names'] = get_wikidata_label_for_property(data, 'P735')
            field_values['surname'] = get_wikidata_label_for_property(data, 'P734')
            field_values['birth_name'] = get_wikidata_label_for_property(data, 'P1477')

            for event, prop in [('birth', 'P569'), ('death', 'P570')]:
                dates = get_nested_object(data, ('statements', prop), None)
                if not dates:
                    continue
                date_index = next((index for index, date in enumerate(dates) if date['rank'] == 'preferred'), 0)
                date = get_nested_object(dates, (date_index, 'value', 'content', 'time', slice(1, 11)), '')
                field_values[f'date_of_{event}'] = next(iter(re.findall(r"^(\d{4})", date)), '')
                # field_values[f'alternative_{event}_date'] = date

            sex = get_wikidata_label_for_property(data, 'P21')
            field_values['sex'] = sex.upper()

            field_values['city_of_birth'] = get_option_from_wikidata_property(data, 'P19', Place)
            field_values['city_of_death'] = get_option_from_wikidata_property(data, 'P20', Place)

        return {k:v for k,v in field_values.items() if v}  # Leave out items with empty values

