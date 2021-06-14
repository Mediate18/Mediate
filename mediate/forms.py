from django import forms
from django_select2.forms import ModelSelect2Widget
from guardian.shortcuts import get_objects_for_user

from catalogues.models import Dataset

class SelectDatasetForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)

        super(SelectDatasetForm, self).__init__(*args, **kwargs)

        datasets = get_objects_for_user(self.user, 'catalogues.change_dataset', Dataset)
        self.fields['dataset'] = forms.ModelChoiceField(
            queryset=datasets,
            widget=ModelSelect2Widget(queryset=datasets, search_fields=['name__icontains'])
        )
