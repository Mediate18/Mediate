from django import forms
from django.urls import reverse_lazy
from django_select2.forms import Select2Widget, ModelSelect2Widget
from viapy.widgets import ViafWidget
from .models import *


class BookFormatModelForm(forms.ModelForm):
    class Meta:
        model = BookFormat
        fields = "__all__"


class ItemModelForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = "__all__"
        widgets = {
            'collection': Select2Widget,
            'lot': Select2Widget,
            'book_format': Select2Widget,
            'binding_material_details': Select2Widget,
            'language': Select2Widget,
            'work': Select2Widget,
        }


class ItemAuthorModelForm(forms.ModelForm):
    class Meta:
        model = ItemAuthor
        fields = "__all__"


class ItemBookFormatRelationModelForm(forms.ModelForm):
    class Meta:
        model = ItemBookFormatRelation
        fields = "__all__"


class ItemItemTypeRelationModelForm(forms.ModelForm):
    class Meta:
        model = ItemItemTypeRelation
        fields = "__all__"


class ItemLanguageRelationModelForm(forms.ModelForm):
    class Meta:
        model = ItemLanguageRelation
        fields = "__all__"
        widgets = {
            'item': ModelSelect2Widget(
                model=Item,
                search_fields=['short_title__icontains']
            ),
            'language': ModelSelect2Widget(
                model=Language,
                search_fields=['name__icontains']
            )
        }


class ItemMaterialDetailsRelationModelForm(forms.ModelForm):
    class Meta:
        model = ItemMaterialDetailsRelation
        fields = "__all__"


class ItemTypeModelForm(forms.ModelForm):
    class Meta:
        model = ItemType
        fields = "__all__"


class ItemWorkRelationModelForm(forms.ModelForm):
    class Meta:
        model = ItemWorkRelation
        fields = "__all__"
        widgets = {
            'item': ModelSelect2Widget(
                model=Item,
                search_fields=['short_title__icontains']
            ),
            'work': ModelSelect2Widget(
                model=Work,
                search_fields=['title__icontains']
            )
        }


class LanguageModelForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = "__all__"


class MaterialDetailsModelForm(forms.ModelForm):
    class Meta:
        model = MaterialDetails
        fields = "__all__"


class PersonItemRelationModelForm(forms.ModelForm):
    class Meta:
        model = PersonItemRelation
        fields = "__all__"
        widgets = {
            'person': ModelSelect2Widget(
                model=Person,
                search_fields=['short_name__icontains']
            ),
            'item': ModelSelect2Widget(
                model=Item,
                search_fields=['short_title__icontains']
            ),
            'role': ModelSelect2Widget(
                model=PersonItemRelationRole,
                search_fields=['name__icontains']
            )
        }


class PersonItemRelationRoleModelForm(forms.ModelForm):
    class Meta:
        model = PersonItemRelationRole
        fields = "__all__"


class PublicationModelForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = "__all__"


class PublisherModelForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = "__all__"


class SubjectModelForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = "__all__"


class WorkModelForm(forms.ModelForm):
    class Meta:
        model = Work
        fields = ['viaf_id', 'title']
        widgets = {
            'viaf_id': ViafWidget(
                url=reverse_lazy('viapy:suggest')
            ),
        }


class WorkAuthorModelForm(forms.ModelForm):
    class Meta:
        model = WorkAuthor
        fields = "__all__"
        widgets = {
            'author': ModelSelect2Widget(
                model=Person,
                search_fields=['short_name__icontains']
            ),
            'work': ModelSelect2Widget(
                model=Work,
                search_fields=['title__icontains']
            ),
        }


class WorkSubjectModelForm(forms.ModelForm):
    class Meta:
        model = WorkSubject
        fields = "__all__"



