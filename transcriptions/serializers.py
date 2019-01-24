from .models import *
from rest_framework import serializers


class SourceMaterialSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SourceMaterial
        fields = "__all__"


class TranscriptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transcription
        fields = "__all__"


class DocumentScanSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DocumentScan
        fields = "__all__"
