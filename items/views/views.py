from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from items.models import Catalogue, CatalogueItem, BookItem

import django_filters


class CatalogueFilter(django_filters.FilterSet):

    class Meta:
        model = Catalogue
        fields = {
            'short_title': ['icontains'],
            'year_of_publication': ['exact', 'lt', 'gt']
        }

class CatalogueDetailView(DetailView):
    model = Catalogue
    template_name = "items/catalogue_detail.html"


class CatalogueItemListView(ListView):

    model = CatalogueItem
    template_name = 'items/catalogueitem_list.html'
    paginate_by = 10


class BookitemListView(ListView):

    model = BookItem
    template_name = 'items/bookitem_list.html'
    paginate_by = 10
