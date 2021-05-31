import json
from django.template import Library


register = Library()


@register.filter
def json_lookup(dictionary, key):
    try:
        value = json.loads(dictionary)[key]
    except (KeyError, TypeError):
        value = ""
    return value
