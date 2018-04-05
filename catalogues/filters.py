import django_filters
from .models import Catalogue

class CatalogueFilter(django_filters.FilterSet):

    class Meta:
        model = Catalogue
        fields = {
            'short_title': ['icontains'],
            'year_of_publication': ['exact', 'lt', 'gt']
        }