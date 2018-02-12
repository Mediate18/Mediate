from django import forms
from items.models import *

class CatalogueModelForm(forms.ModelForm):
    class Meta:
        model = Catalogue
        fields = "__all__"