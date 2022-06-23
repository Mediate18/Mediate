from django.template import Library
from django.conf import settings


register = Library()


# settings value
@register.filter
def settings_value(name):
    return getattr(settings, name, "")