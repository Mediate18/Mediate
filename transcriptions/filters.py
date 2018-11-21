import django_filters
from .models import *


# DocumentScan filter
class DocumentScanFilter(django_filters.FilterSet):
    class Meta:
        model = DocumentScan
        fields = ['transcription']


# SourceMaterial filter
class SourceMaterialFilter(django_filters.FilterSet):
    class Meta:
        model = SourceMaterial
        exclude = ['uuid']


# Transcription filter
class TranscriptionFilter(django_filters.FilterSet):
    class Meta:
        model = Transcription
        exclude = ['uuid']

