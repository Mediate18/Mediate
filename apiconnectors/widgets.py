from dal import autocomplete
from django.utils.safestring import mark_safe


class ApiSelectWidget(autocomplete.Select2):
    '''Custom autocomplete select widget that displays the selection as a link if possible.
    Extends :class:`dal.autocomplete.Select2`.'''

    def render(self, name, value, attrs=None):
        # select2 filters based on existing choices (non-existent here),
        # so when a value is set, add it to the list of choices
        if value:
            self.choices = [(value, value)]
        widget = super(ApiSelectWidget, self).render(name, value, attrs)
        return mark_safe(
            '%s<p><br /><a id="%s_uri" target="_blank" href="%s">%s</a></p>' % \
            (widget, name, value or '', value or ''))


