import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from .models import Item


class ItemTable(tables.Table):
    lot = tables.LinkColumn('lot_detail', args=[A('pk')])
    sales_price = tables.LinkColumn('item_detail', args=[A('pk')])

    class Meta:
        model = Item
        fields = ('collection', 'lot', 'number_of_volumes', 'sales_price', 'book_format',
                    'binding_material_details', 'language', 'work', 'buyer')
        attrs = {'class': 'table table-sortable'}