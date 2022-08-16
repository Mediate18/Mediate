import django_tables2 as tables
from django.utils.html import format_html
from .models import *
from mediate.columns import ActionColumn
from django.utils.translation import ugettext_lazy as _


# DocumentScan table
class DocumentScanTable(tables.Table):
    uuid = ActionColumn('documentscan_detail', 'change_documentscan', 'delete_documentscan', orderable=False)

    class Meta:
        model = DocumentScan
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'transcription',
            'scan',
            'uuid'
        ]


# SourceMaterial table
class SourceMaterialTable(tables.Table):
    uuid = ActionColumn('sourcematerial_detail', 'change_sourcematerial', 'delete_sourcematerial', orderable=False)

    class Meta:
        model = SourceMaterial
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'uuid'
        ]


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


# ShelfMark table
class ShelfMarkTable(tables.Table):
    uuid = ActionColumn('shelfmark_detail', 'change_shelfmark', 'delete_shelfmark', orderable=False)
    collection = tables.Column(empty_values=(), orderable=False, verbose_name=_("Collections"))

    class Meta:
        model = ShelfMark
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'place',
            'library',
            'text',
            'collection',
            'uuid'
        ]

    def render_collection(self, record):
        collections = []
        for collection in record.collection_set.values('short_title', 'uuid'):
            collections.append("<a href='{}'>{}</a>".format(reverse_lazy('collection_detail', args=[collection['uuid']]), collection['short_title']))
        return format_html(", ".join(collections))
