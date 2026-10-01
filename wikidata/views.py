import requests

from django.apps import apps
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import translation, html
from django_select2.views import AutoResponseView
from requests import Response

from persons.models import Country, Place
from wikidata.utils import get_nested_object
from wikidata.wikidata_api import get_wikidata_label, get_wikidata_statements


def get_wikidata_label_translations(api_id, field_name):
    field_values = {}
    for language_code, _ in settings.LANGUAGES:
        response, request_failed = get_wikidata_label(api_id, language_code)
        if not request_failed and response.status_code == requests.codes.ok:
            field_values[field_name] = response.json()
    return field_values


def get_wikidata_label_for_property(data, property, index=0, language='en'):
    id = get_nested_object(data, ('statements', property, index, 'value', 'content'), None)
    if not id:
        return ''
    response, request_failed = get_wikidata_label(id, language)
    return response.json() if (not request_failed and response.status_code == requests.codes.ok) else ''


def get_or_create_object_from_wikidata_id(wikidata_id, property, model):
    if data := get_wikidata_statements(wikidata_id):
        return get_option_from_wikidata_property(data, property, model).get('id', None)
    return None


# Which field holds the name value of the model:
name_field_names = {Country: Country.name.field.name, Place: Place.name.field.name}


def create_object_from_wikidata_id(model, wikidata_id):
    if model not in name_field_names.keys():
        return None
    field_values = get_wikidata_label_translations(wikidata_id, name_field_names[model])
    field_values['wikidata_id'] = wikidata_id
    if model == Place and (data := get_wikidata_statements(wikidata_id)):
        field_values['latitude'] = round(get_nested_object(data, ('statements', 'P625', 0, 'value', 'content', 'latitude')), 6)
        field_values['longitude'] = round(get_nested_object(data, ('statements', 'P625', 0, 'value', 'content', 'longitude')), 6)
        field_values['country_id'] = get_or_create_object_from_wikidata_id(wikidata_id, 'P17', Country)
    return model.objects.create(**field_values)


def get_option_from_wikidata_property(data, prop, model):
    property_object = get_nested_object(data, ('statements', prop), None)
    if type(property_object) is not list:
        return {}

    # Get the first object that has 'rank': 'preferred', otherwise get the first in the list
    index = next((index for index, obj in enumerate(property_object) if obj.get('rank') == 'preferred'), 0)
    wikidata_id = get_nested_object(property_object, (index, 'value', 'content'), None)
    if not wikidata_id:
        return {}

    label = get_wikidata_label_for_property(data, prop, index=index)
    if obj := model.objects.filter(Q(wikidata_id=wikidata_id) | Q(**{name_field_names[model]: label})).first():
        return {'text': str(obj), 'id': obj.pk}
    if obj := create_object_from_wikidata_id(model, wikidata_id):
        return {'text': str(obj), 'id': obj.pk}
    return {}


def request_wikidata_suggest(term: str, page: int=1, limit: int=10) -> Response:
    api_key = settings.WIKIDATA_API_KEY
    language_code = translation.get_language()
    offset = (page - 1) * limit

    return requests.get(settings.WIKIDATA_SUGGEST_URL,
                        params={'q': term, 'language': language_code, 'limit': limit, 'offset': offset},
                        headers={'accept': 'application/json', 'Authorization': f'Bearer {api_key}'})


class WikidataSuggestView(AutoResponseView):
    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '')
        page = request.GET.get('page', '1')
        page = int(page) if page.isdigit() else 1
        limit = 10
        response = request_wikidata_suggest(term, page, limit)

        if response.status_code != requests.codes.ok:
            return JsonResponse({'results': {}, 'more': False})

        results = [
            {'id': html.escape(item['id']), 'text': self.render_text(item)}
            for item in response.json().get('results', [])
        ]

        return JsonResponse({
            'results': results,
            'more': len(results) >= limit
        })

    @staticmethod
    def render_text(item):
        id = html.escape(item['id'])
        label = html.escape(item['display-label']['value'])
        description = html.escape(item['description']['value'] if item['description'] else '')
        return f"""
            <div>
                <b>{label}</b>
                <span style='color: dimgray; margin-left: auto; margin-right: 0'>{id}</span>
                <br/>
                <small>{description}</small>
            </div>
        """


class ObjectExistsWikidataView(AutoResponseView):
    """Returns whether an object exists given the model name and Wikidata ID"""
    def get(self, request, app_label, model_name, wikidata_id):
        model = apps.get_model(app_label=app_label, model_name=model_name)
        first = model.objects.filter(wikidata_id=wikidata_id).first()
        return JsonResponse({
            'exists': first is not None,
            'href': reverse_lazy(f'admin:{first._meta.app_label}_{first._meta.model_name}_change', args=(first.pk,)) if first else '',
        })