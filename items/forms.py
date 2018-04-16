from django import forms
from django_select2.forms import Select2Widget
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
        fields = "__all__"


class WorkAuthorModelForm(forms.ModelForm):
    class Meta:
        model = WorkAuthor
        fields = "__all__"


class WorkSubjectModelForm(forms.ModelForm):
    class Meta:
        model = WorkSubject
        fields = "__all__"



