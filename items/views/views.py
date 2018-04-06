from django.contrib import messages
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView

from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy
import django_tables2

from ..models import Lot, Item
from ..forms import ItemModelForm
from ..filters import ItemFilter
from ..tables import ItemTable


class LotListView(ListView):
    model = Lot
    template_name = 'items/lot_list.html'
    paginate_by = 10


# Item views
class ItemTableView(ListView):
    model = Item

    def get_context_data(self, **kwargs):
        context = super(ItemTableView, self).get_context_data(**kwargs)
        filter = ItemFilter(self.request.GET, queryset=self.object_list)

        table = ItemTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        return context


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
    fields = ItemModelForm
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
# end Item views
