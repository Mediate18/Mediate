import django_filters
from .models import Item


class ItemFilter(django_filters.FilterSet):
    sales_price = django_filters.NumericRangeFilter()  # TODO sales_price is not an Integer field in the model
    class Meta:
        model = Item
        fields = ['sales_price']