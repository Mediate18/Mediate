import django_filters
from items.models import Catalogue

class CatalogueFilter(django_filters.FilterSet):

    class Meta:
        model = Catalogue
        fields = {
            'short_title': ['icontains'],
            'year_of_publication': ['exact', 'lt', 'gt']
        }