from django import forms
from django.urls import reverse_lazy
from django_select2.forms import Select2Widget, ModelSelect2Widget, ModelSelect2MultipleWidget
from django_date_extensions.fields import ApproximateDateFormField
from django.forms import inlineformset_factory
from apiconnectors.widgets import ApiSelectWidget
from .models import *


class PersonModelForm(forms.ModelForm):
    suggest_select_ids = ['viaf_id', 'publisher_cerl_id', 'city_of_birth', 'city_of_death']  # IDs of the suggest widgets

    class Meta:
        model = Person
        fields = "__all__"
        widgets = {
            'viaf_id': ApiSelectWidget(
                url=reverse_lazy('person_viaf_suggest'),
                attrs={'data-html': True,
                       'data-placeholder': "Search for a person"},
            ),
            'publisher_cerl_id': ApiSelectWidget(
                url='cerl_suggest_person',
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_religious_affiliation_field()
        self.add_person_profession_field()

    def add_religious_affiliation_field(self):
        religions = forms.ModelMultipleChoiceField(
            label="Religions",
            widget=ModelSelect2MultipleWidget(
                model=Religion,
                search_fields=['name__icontains'],
            ),
            queryset=Religion.objects.all(),
            required=False,
            initial=Religion.objects.filter(religiousaffiliation__person=self.instance)
        )
        self.fields['religions'] = religions

    def add_person_profession_field(self):
        professions = forms.ModelMultipleChoiceField(
            label="Professions",
            widget=ModelSelect2MultipleWidget(
                model=Profession,
                search_fields=['name__icontains'],
            ),
            queryset=Profession.objects.all(),
            required=False,
            initial=Profession.objects.filter(personprofession__person=self.instance)
        )
        self.fields['professions'] = professions

    def save(self, commit=True):
        self.instance = super().save(commit=commit)
        if commit:
            self.save_religions()
            self.save_professions()
        return self.instance

    def save_religions(self):
        submitted_religions = self.cleaned_data['religions']

        # Delete relations for religions that are not in the submitted religions
        relations_to_delete = ReligiousAffiliation.objects \
            .filter(person=self.instance).exclude(religion__in=submitted_religions)
        for relation in relations_to_delete:
            relation.delete()

        # Add relations for submitted religions that are not in the existing religions
        new_religions = set(submitted_religions) - set(Religion.objects.filter(
            religiousaffiliation__person=self.instance))
        for religion in new_religions:
            religious_affiliation = ReligiousAffiliation(person=self.instance, religion=religion)
            religious_affiliation.save()

    def save_professions(self):
        submitted_professions = self.cleaned_data['professions']

        # Delete relations for professions that are not in the submitted professions
        relations_to_delete = PersonProfession.objects \
            .filter(person=self.instance).exclude(profession__in=submitted_professions)
        for relation in relations_to_delete:
            relation.delete()

        # Add relations for submitted professions that are not in the existing professions
        new_professions = set(submitted_professions) - set(Profession.objects.filter(
            personprofession__person=self.instance))
        for profession in new_professions:
            person_profession = PersonProfession(person=self.instance, profession=profession)
            person_profession.save()


class AlternativePersonNameForm(forms.ModelForm):
    class Meta:
        model = AlternativePersonName
        fields = "__all__"


AlternativePersonNameFormSet = inlineformset_factory(Person, AlternativePersonName, form=AlternativePersonNameForm,
                                                     can_delete=True, extra=1)


class PersonPersonRelationModelForm(forms.ModelForm):
    class Meta:
        model = PersonPersonRelation
        fields = (
            'first_person',
            'type',
            'second_person',
            'start_year',
            'end_year'
        )
        widgets = {
            'first_person': ModelSelect2Widget(
                label="Person",
                model=Person,
                search_fields=['short_name__icontains']
            ),
            'second_person': ModelSelect2Widget(
                label="Person",
                model=Person,
                search_fields=['short_name__icontains'],
                attrs={'style': 'width: 200px;'}
            ),
            'type': ModelSelect2Widget(
                model=PersonPersonRelationType,
                search_fields=['name__icontains'],
                attrs={'style': 'width: 150px;'}
            )
        }


FirstPersonPersonRelationFormSet = inlineformset_factory(Person, PersonPersonRelation, fk_name='first_person',
                                                         form=PersonPersonRelationModelForm, can_delete=True, extra=1)

SecondPersonPersonRelationFormSet = inlineformset_factory(Person, PersonPersonRelation, fk_name='second_person',
                                                         form=PersonPersonRelationModelForm, can_delete=True, extra=1)


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
    suggest_select_ids = ['cerl_id']

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

    class Media:
        js = ('js/viaf_select.js',)


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
        widgets = {
            'person': ModelSelect2Widget(
                model=Person,
                search_fields=['short_name__icontains', 'surname__icontains', 'first_names__icontains']
            ),
            'place': ModelSelect2Widget(
                model=Place,
                search_fields=['name__icontains'],
                attrs={'style': 'width: 300px'}
            )
        }


ResidenceFormSet = inlineformset_factory(Person, Residence, form=ResidenceModelForm, can_delete=True, extra=1)
