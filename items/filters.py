import django_filters
from .models import *


class ItemFilter(django_filters.FilterSet):
    sales_price = django_filters.NumericRangeFilter()  # TODO sales_price is not an Integer field in the model
    class Meta:
        model = Item
        fields = ['sales_price']


class LanguageFilter(django_filters.FilterSet):
    class Meta:
        model = Language
        fields = "__all__"