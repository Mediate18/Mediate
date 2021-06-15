from django.template import Library
from catalogues.tools import get_datasets_for_session


register = Library()

@register.filter
def get_datasets(request):
    return get_datasets_for_session(request)