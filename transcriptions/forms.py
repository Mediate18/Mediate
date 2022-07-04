from django import forms
from django_select2.forms import Select2Widget, ModelSelect2Widget, ModelSelect2MultipleWidget
from .models import *
from catalogues.models import Library, Collection


class DocumentScanModelForm(forms.ModelForm):
    class Meta:
        model = DocumentScan
        fields = "__all__"


class SourceMaterialModelForm(forms.ModelForm):
    class Meta:
        model = SourceMaterial
        fields = "__all__"


class TranscriptionModelForm(forms.ModelForm):
    class Meta:
        model = Transcription
        fields = ['source_material', 'curator']
        widgets = {
            'source_material': Select2Widget,
        }


class ShelfMarkModelForm(forms.ModelForm):
    collection = forms.ModelMultipleChoiceField(
        queryset=Collection.objects.all(),
        widget=ModelSelect2MultipleWidget(
            model=Collection,
            search_fields=['short_title__icontains'],
            attrs={'data-placeholder': "Select multiple"},
        ),
    )

    class Meta:
        model = ShelfMark
        # fields = ['place', 'library']
        exclude = ['uuid']
        widgets = {
            'place': ModelSelect2Widget(
                model=Place,
                search_fields=['name__icontains'],
                attrs={'data-placeholder': "Select multiple"},
            ),
            'library': ModelSelect2Widget(
                model=Library,
                search_fields=['name__icontains'],
                attrs={'data-placeholder': "Select multiple"},
            ),
        }

