from django import forms
from django_select2.forms import Select2Widget
from items.models import *


class CatalogueModelForm(forms.ModelForm):
    class Meta:
        model = Catalogue
        fields = "__all__"
        widgets = {
            'collection': Select2Widget,
            'type': Select2Widget,
            'transcription': Select2Widget,
        }
