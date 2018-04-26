from django import forms
from .models import *


class PersonModelForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = "__all__"


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


class PlaceModelForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = "__all__"


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

