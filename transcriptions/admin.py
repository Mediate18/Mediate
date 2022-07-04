from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import *


@admin.register(DocumentScan)
class DocumentScanAdmin(SimpleHistoryAdmin):
    pass


@admin.register(SourceMaterial)
class SourceMaterialAdmin(SimpleHistoryAdmin):
    pass


@admin.register(Transcription)
class TranscriptionAdmin(SimpleHistoryAdmin):
    pass


@admin.register(ShelfMark)
class ShelfMarkAdmin(SimpleHistoryAdmin):
    pass
