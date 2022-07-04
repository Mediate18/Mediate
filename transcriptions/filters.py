import django_filters
from django_filters import ModelMultipleChoiceFilter
from django_select2.forms import ModelSelect2MultipleWidget
from .models import *
from catalogues.models import Library


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


# ShelfMark filter
class ShelfMarkFilter(django_filters.FilterSet):
    place = ModelMultipleChoiceFilter(
        queryset=Place.objects.all(),
        widget=ModelSelect2MultipleWidget(
            model=Place,
            search_fields=['name__icontains'],
            attrs={'data-placeholder': "Select multiple"},
        ),
    )
    library = ModelMultipleChoiceFilter(
        queryset=Library.objects.all(),
        widget=ModelSelect2MultipleWidget(
            model=Library,
            search_fields=['name__icontains'],
            attrs={'data-placeholder': "Select multiple"},
        ),
    )

    class Meta:
        model = ShelfMark
        fields = ['place', 'library', 'text']

