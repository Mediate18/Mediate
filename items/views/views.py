from django.contrib import messages
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView

from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy

from ..models import Lot, Item
from ..forms import ItemModelForm


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


class ItemCreateView(CreateView):
    model = Item
    template_name = 'generic_form.html'
    form_class = ItemModelForm
    success_url = reverse_lazy('items')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "item"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class ItemUpdateView(UpdateView):
    model = Item
    template_name = 'generic_form.html'
    fields = "__all__"
# end Item views
