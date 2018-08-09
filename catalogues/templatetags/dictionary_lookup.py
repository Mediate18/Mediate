from django.template import Library

register = Library()


@register.filter
def lookup(dictionary, key):
    try:
        value = dictionary[key]
    except KeyError:
        value = ""
    return value
