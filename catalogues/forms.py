from django import forms
from django_select2.forms import Select2Widget, ModelSelect2Widget
from .models import *


class CatalogueModelForm(forms.ModelForm):
    class Meta:
        model = Catalogue
        fields = "__all__"
        widgets = {
            'collection': Select2Widget,
            'type': Select2Widget,
            'transcription': Select2Widget,
        }


class CatalogueHeldByModelForm(forms.ModelForm):
    class Meta:
        model = CatalogueHeldBy
        fields = "__all__"


class CatalogueTypeModelForm(forms.ModelForm):
    class Meta:
        model = CatalogueType
        fields = "__all__"


class CollectionModelForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = "__all__"


class CollectionYearModelForm(forms.ModelForm):
    class Meta:
        model = CollectionYear
        fields = "__all__"


class LibraryModelForm(forms.ModelForm):
    class Meta:
        model = Library
        fields = "__all__"


class LotModelForm(forms.ModelForm):
    class Meta:
        model = Lot
        fields = "__all__"
        widgets = {
            'catalogue': ModelSelect2Widget(
                model=Catalogue,
                search_fields=['name__icontains']
            ),
        }


class PersonCatalogueRelationModelForm(forms.ModelForm):
    class Meta:
        model = PersonCatalogueRelation
        fields = "__all__"


class PersonCatalogueRelationRoleModelForm(forms.ModelForm):
    class Meta:
        model = PersonCatalogueRelationRole
        fields = "__all__"


class PersonCollectionRelationModelForm(forms.ModelForm):
    class Meta:
        model = PersonCollectionRelation
        fields = "__all__"


