from django.views.generic.list import ListView

from ..models import Lot, Item


# Catalogue detail views
class LotListView(ListView):

    model = Lot
    template_name = 'items/lot_list.html'
    paginate_by = 10
# end Catalogue detail views


# Item views
class ItemListView(ListView):

    model = Item
    template_name = 'items/item_list.html'
    paginate_by = 10
# end Item views
