import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from .models import *
from mediate.columns import ActionColumn


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
    uuid = ActionColumn('transcription_detail', 'change_transcription', 'delete_transcription', orderable=False)

    class Meta:
        model = Transcription
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'source_material',
            'curator',
            'author',
            'date',
            'uuid'
        ]


