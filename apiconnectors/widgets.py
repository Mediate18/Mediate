from dal import autocomplete
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import escape

from apiconnectors.cerlapi import cerl_record_url, get_record


class ApiSelectWidget(autocomplete.Select2):
    '''Custom autocomplete select widget that displays the selection as a link if possible.
    Extends :class:`dal.autocomplete.Select2`.'''

    def __init__(self, model=None, *args, **kwargs):
        super(autocomplete.Select2, ApiSelectWidget).__init__(self, *args, **kwargs)
        self.model=model

    def render(self, name, value, attrs=None, renderer=None):
        # select2 filters based on existing choices (non-existent here),
        # so when a value is set, add it to the list of choices
        id = value
        url = value
        if value:
            if isinstance(url, str) and (url.startswith('cnl') or url.startswith('cni')):
                choice = get_record(value)
            else:
                choice = value

            self.choices = [(id, choice)]
            if self.model:
                try:
                    obj = self.model.objects.get(pk=value)
                    value = str(obj)
                    self.choices = [(obj.pk, value)]
                    url = obj.get_absolute_url()
                except ObjectDoesNotExist:
                    pass
            if url.startswith('cnl') or url.startswith('cni'):
                url = cerl_record_url + url
        widget = super(ApiSelectWidget, self).render(name, id, attrs)
        return mark_safe(
            '%s<p><br /><a id="%s_uri" target="_blank" href="%s">%s</a></p>' % \
            (widget, name, url or '', escape(value or '')))
