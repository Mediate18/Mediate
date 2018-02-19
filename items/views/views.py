from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from items.models import Catalogue, CatalogueEntry, Item
from items.forms import CatalogueModelForm

import django_filters


# Catalogue views
class CatalogueFilter(django_filters.FilterSet):

    class Meta:
        model = Catalogue
        fields = {
            'short_title': ['icontains'],
            'year_of_publication': ['exact', 'lt', 'gt']
        }


def change_catalogue(request, pk):
    catalogue = get_object_or_404(Catalogue, pk=pk)

    # Check for a pending moderation (status == 2)
    if catalogue.moderated_object is not None and catalogue.moderated_object.status == 2:
        messages.add_message(request, messages.ERROR, _("This catalogue is being reviewed by a moderator."))
        return redirect('catalogue_detail', pk=pk)  # Redirect to the catalogue detail view

    if request.method == 'POST':
        form = CatalogueModelForm(request.POST)
        if form.is_valid():
            form = CatalogueModelForm(request.POST, instance=catalogue)
            form.save()

            if not request.user.is_superuser:
                messages.add_message(request, messages.SUCCESS,
                                     _("Your changes will be sent to a moderator for reviewing."))

            return redirect('catalogues') # Redirect to the catalogues overview

    form = CatalogueModelForm(instance=catalogue)
    return render(request, "items/generic_form.html", {"form": form, "user": request.user,
                                                         "action": "change", "object_name": "catalogue"})


def add_catalogue(request):
    if request.method == 'POST':
        form = CatalogueModelForm(request.POST)
        if form.is_valid():
            form = CatalogueModelForm(request.POST)
            form.save()

            if not request.user.is_superuser:
                messages.add_message(request, messages.SUCCESS,
                                     _("Your changes will be sent to a moderator for reviewing."))

            return redirect('catalogues') # Redirect to the catalogues overview

    form = CatalogueModelForm()
    return render(request, "items/generic_form.html", {"form": form, "user": request.user,
                                                         "action": "add", "object_name": "catalogue"})

def delete_catalogue(request, pk):
    catalogue = get_object_or_404(Catalogue, pk=pk)

    # Check for a pending moderation (status == 2)
    if catalogue.moderated_object is not None and catalogue.moderated_object.status == 2:
        messages.add_message(request, messages.ERROR, _("This catalogue is being reviewed by a moderator."))
        return redirect('catalogue_detail', pk=pk)  # Redirect to the catalogue detail view

    try:
        catalogue.delete()
        messages.add_message(request, messages.SUCCESS, _("This catalogue is being reviewed by a moderator."))
    except:
        messages.add_message(request, messages.ERROR, _("The catalogue could not be deleted."))
    return redirect('catalogues')  # Redirect to the catalogues overview



class CatalogueDetailView(DetailView):
    model = Catalogue
    template_name = "items/catalogue_detail.html"
# end Catalogue views


# Catalogue detail views
class CatalogueEntryListView(ListView):

    model = CatalogueEntry
    template_name = 'items/catalogueentry_list.html'
    paginate_by = 10
# end Catalogue detail views


# Item views
class ItemListView(ListView):

    model = Item
    template_name = 'items/item_list.html'
    paginate_by = 10
# end Item views
