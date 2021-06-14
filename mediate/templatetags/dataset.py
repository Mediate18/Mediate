from django.template import Library
from catalogues.tools import get_dataset_for_user


register = Library()

@register.filter
def get_dataset_name(request):
    dataset = get_dataset_for_user(request)
    if dataset:
        return dataset.name
    else:
        return "NO DATASET SELECTED"