from django import forms
from django_select2.forms import ModelSelect2MultipleWidget
from guardian.shortcuts import get_objects_for_user

from catalogues.models import Dataset
from catalogues.tools import get_dataset_for_anonymoususer

class SelectDatasetForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)

        super(SelectDatasetForm, self).__init__(*args, **kwargs)

        datasets = get_objects_for_user(self.request.user, 'catalogues.change_dataset', Dataset)

        if 'datasets' in self.request.session:
            selected_datasets = [dataset['uuid'] for dataset in self.request.session['datasets']]
        else:
            selected_datasets = [get_dataset_for_anonymoususer()]


        self.fields['datasets'] = forms.ModelMultipleChoiceField(
            initial=selected_datasets,
            queryset=datasets,
            widget=ModelSelect2MultipleWidget(queryset=datasets, search_fields=['name__icontains'])
        )
