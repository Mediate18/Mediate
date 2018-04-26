import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from .models import *


# DocumentScan table
class DocumentScanTable(tables.Table):
    edit = tables.LinkColumn('change_documentscan', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = DocumentScan
        attrs = {'class': 'table table-sortable'}


# SourceMaterial table
class SourceMaterialTable(tables.Table):
    edit = tables.LinkColumn('change_sourcematerial', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = SourceMaterial
        attrs = {'class': 'table table-sortable'}


# Transcription table
class TranscriptionTable(tables.Table):
    edit = tables.LinkColumn('change_transcription', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Transcription
        attrs = {'class': 'table table-sortable'}


