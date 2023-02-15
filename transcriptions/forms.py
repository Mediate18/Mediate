from django import forms
from django_select2.forms import Select2Widget, ModelSelect2Widget, ModelSelect2MultipleWidget
from .models import *
from catalogues.models import Library, Catalogue


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

    def __init__(self, **kwargs):
        self.catalogue = kwargs.pop('catalogue', None)
        super().__init__(**kwargs)
        self.add_catalogue_field()

    def add_catalogue_field(self):
        catalogue = forms.ModelMultipleChoiceField(
            queryset=self.catalogue,
            widget=ModelSelect2MultipleWidget(
                queryset=self.catalogue,
                search_fields=['short_title__icontains'],
                attrs={'data-placeholder': "Select multiple"},
            ),
            initial=Catalogue.objects.filter(shelf_mark=self.instance)
        )
        self.fields['catalogue'] = catalogue

