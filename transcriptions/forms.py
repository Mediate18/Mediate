from django import forms
from django_select2.forms import Select2Widget
from .models import *


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
        fields = "__all__"


