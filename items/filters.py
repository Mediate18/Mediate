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

    def __init__(self, data=None, queryset=None, prefix=None, strict=None, request=None):
        queryset = Language.unmoderated_objects.all()
        super(LanguageFilter, self).__init__(data=data, queryset=queryset, prefix=prefix, strict=strict, request=request)

    # @property
    # def qs(self):
    #     self.queryset = Language.unmoderated_objects.all()
    #     return super(LanguageFilter, self).qs