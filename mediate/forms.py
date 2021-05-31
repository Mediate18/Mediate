from django import forms
from django_select2.forms import ModelSelect2Widget

from catalogues.models import Dataset

class SelectDatasetForm(forms.Form):
    dataset = forms.ModelChoiceField(
        queryset=Dataset.objects.all(),
        widget=ModelSelect2Widget(model=Dataset, search_fields=['name__icontains'])
    )
