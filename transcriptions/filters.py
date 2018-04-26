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
        fields = "__all__"


# Transcription filter
class TranscriptionFilter(django_filters.FilterSet):
    class Meta:
        model = Transcription
        fields = "__all__"


