from django.contrib import admin
from .models import *


@admin.register(DocumentScan)
class DocumentScanAdmin(admin.ModelAdmin):
    pass


@admin.register(SourceMaterial)
class SourceMaterialAdmin(admin.ModelAdmin):
    pass


@admin.register(Transcription)
class TranscriptionAdmin(admin.ModelAdmin):
    pass
