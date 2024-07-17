from rest_framework import viewsets
from ..serializers import *


class SourceMaterialViewSet(viewsets.ModelViewSet):
    queryset = SourceMaterial.objects.all()
    serializer_class = SourceMaterialSerializer
    http_method_names = ['get']


class TranscriptionViewSet(viewsets.ModelViewSet):
    queryset = Transcription.objects.all()
    serializer_class = TranscriptionSerializer
    http_method_names = ['get']


class DocumentScanViewSet(viewsets.ModelViewSet):
    queryset = DocumentScan.objects.all()
    serializer_class = DocumentScanSerializer
    http_method_names = ['get']


class ShelfmarkViewSet(viewsets.ModelViewSet):
    queryset = ShelfMark.objects.all()
    serializer_class = ShelfmarkSerializer
    http_method_names = ['get']
