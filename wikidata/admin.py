from dataclasses import dataclass, astuple

import requests
from django.conf import settings
from django.db import models
from django.utils import html, translation
from django.utils.safestring import mark_safe
from django_select2.forms import HeavySelect2Widget

from wikidata.wikidata_api import get_wikidata_label


@dataclass
class ApiInfo:
    obj: object
    model: models.Model
    model_field_name: str
    url_template: str
    api_name: str
    fill_field_name: str


class ApiSelectWidget(HeavySelect2Widget):
    css_class_name = 'django-select2 django-select2-apilink'
    js = 'wikidata/js/apilink.js'

    def __init__(self, *args, **kwargs):
        self.api_info = kwargs.pop('api_info', None)
        super().__init__(*args, **kwargs)

    def render(self, *args, **kwargs):
        output =  super().render(*args, **kwargs)
        obj, model, model_field_name, url_template, api_name, fill_field_name = astuple(self.api_info)
        api_id, display_style = ("", "display: none") if not obj or not getattr(obj, model_field_name, None) \
                                else (html.escape(getattr(obj, model_field_name)), "")

        return output + mark_safe(f"""
            <div id='api_block_{model_field_name}' style="margin: 4px 0 0 10px;{display_style}">
                <a id="apilink_{model_field_name}" href="{url_template.format(api_id)}" target="_blank"
                 href_base="{url_template[:-2]}">
                    Show on {api_name}
                </a>
                <button class="button fill-button" id="fillbutton_{model_field_name}" data-fill-field-name="{fill_field_name}" 
                type="button">Fill in</button>
            </div>
            <div id='api_object_exists_{model_field_name}' style="display: none;"
                 data-django-applabel="{model._meta.app_label}"
                 data-django-model="{model.__name__}">
                <p style="color: red; margin: .4em 1em 0em 1em">
                    A {model.__name__.lower()} with this Wikidata ID already exists.
                    <a href="" target="_blank" style="margin-left:1em">
                        <img src="/static/admin/img/icon-viewlink.svg" alt="View"> View that {model.__name__.lower()}
                    </a>
                </p>
            </div>
            <script src="{settings.STATIC_URL}{self.js}"></script>
        """)


class WikidataAdminMixin:
    class Media:
        css = {
            'all': ('wikidata/css/admin/wikidata_id.css', 'admin/css/vendor/select2/select2.css')
        }

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        api_info = ApiInfo(obj, self.model, 'wikidata_id', settings.WIKIDATA_URL, 'Wikidata',
                           fill_field_name=self.fill_field_name)

        if not obj:
            form.base_fields['wikidata_id'].widget = ApiSelectWidget(data_view='wikidata', api_info=api_info)
            return form

        if not 'wikidata_id' in form.base_fields.keys():
            return form

        response, request_failed = get_wikidata_label(obj.wikidata_id, translation.get_language())
        request_with_language = True
        if request_failed or response.status_code != requests.codes.ok:
            response, request_failed = get_wikidata_label(obj.wikidata_id, '')
            request_with_language = False

        if request_failed or response.status_code != requests.codes.ok:
            label = obj.wikidata_id
            description = "Data could not be fetched from WikiData."
        else:
            label = str(response.json()) if request_with_language else response.json().get('mul', 'No WikiData label.')
            description = obj.wikidata_id

        text = f"""
            <div>
                <b>{label}</b>
                <br/>
                <small>{description}</small>
            </div>
        """

        form.base_fields['wikidata_id'].widget = ApiSelectWidget(data_view='wikidata', api_info=api_info,
                                                                 choices=[(obj.wikidata_id, text)])
        return form

    def wikidata_link(self, obj):
        wikidata_id = html.escape(obj.wikidata_id)
        return mark_safe(f'<a href="https://www.wikidata.org/wiki/{wikidata_id}">{wikidata_id}</a>')
