from django import forms
from django.urls import reverse_lazy
from django_select2.forms import Select2Widget, ModelSelect2Widget
from django_date_extensions.fields import ApproximateDateFormField
from apiconnectors.widgets import ApiSelectWidget
from viapy.widgets import ViafWidget
from .models import *


class PersonModelForm(forms.ModelForm):
    suggest_select_ids = ['viaf_id', 'city_of_birth', 'city_of_death']  # IDs of the suggest widgets

    class Meta:
        model = Person
        fields = "__all__"
        widgets = {
            'viaf_id': ApiSelectWidget(
                url=reverse_lazy('person_viaf_suggest'),
                attrs={'data-html': True,
                       'data-placeholder': "Search for a person"},
            ),
            'sex': Select2Widget,
            'city_of_birth': ApiSelectWidget(
                url='placeandcerl_suggest',
                attrs={'data-html': True,
                       'data-placeholder': "Search for a place - <i>italic: places in the local database</i>"},
                model=Place,
            ),
            'city_of_death': ApiSelectWidget(
                url='placeandcerl_suggest',
                attrs={'data-html': True,
                       'data-placeholder': "Search for a place - <i>italic: places in the local database</i>"},
                model=Place,
            ),
        }

    class Media:
        js = ('js/viaf_select.js',)

class PersonPersonRelationModelForm(forms.ModelForm):
    class Meta:
        model = PersonPersonRelation
        fields = "__all__"


class PersonPersonRelationTypeModelForm(forms.ModelForm):
    class Meta:
        model = PersonPersonRelationType
        fields = "__all__"


class PersonProfessionModelForm(forms.ModelForm):
    class Meta:
        model = PersonProfession
        fields = "__all__"


class CountryModelForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = "__all__"


class PlaceModelForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = "__all__"
        widgets = {
            'cerl_id': ApiSelectWidget(
                url='cerl_suggest',
                attrs={'data-html': True,
                       'data-placeholder': "Search for a place"},
            ),
            'country': ModelSelect2Widget(
                model=Country,
                search_fields=['name__icontains']
            )
        }


class ProfessionModelForm(forms.ModelForm):
    class Meta:
        model = Profession
        fields = "__all__"


class ReligionModelForm(forms.ModelForm):
    class Meta:
        model = Religion
        fields = "__all__"


class ReligiousAffiliationModelForm(forms.ModelForm):
    class Meta:
        model = ReligiousAffiliation
        fields = "__all__"


class ResidenceModelForm(forms.ModelForm):
    class Meta:
        model = Residence
        fields = "__all__"


