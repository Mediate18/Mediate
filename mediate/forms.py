from django import forms
from django_select2.forms import ModelSelect2MultipleWidget
from guardian.shortcuts import get_objects_for_user

from catalogues.models import Dataset

class SelectDatasetForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)

        super(SelectDatasetForm, self).__init__(*args, **kwargs)

        datasets = get_objects_for_user(self.request.user, 'catalogues.change_dataset', Dataset)
        self.fields['datasets'] = forms.ModelMultipleChoiceField(
            initial=[dataset['uuid'] for dataset in self.request.session['datasets']]  ,
            queryset=datasets,
            widget=ModelSelect2MultipleWidget(queryset=datasets, search_fields=['name__icontains'])
        )
