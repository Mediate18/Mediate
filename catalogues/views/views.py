from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from ..forms import *
from ..tables import *
from ..filters import *

from ..models import *

import django_tables2


# Catalogue views
class CatalogueTableView(ListView):
    model = Catalogue
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Catalogue.objects.all()

    def get_context_data(self, **kwargs):
        context = super(CatalogueTableView, self).get_context_data(**kwargs)
        filter = CatalogueFilter(self.request.GET, queryset=self.get_queryset())

        table = CatalogueTable(filter.qs)
        django_tables2.RequestConfig(self.request, paginate={'per_page': 10}).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "catalogue"
        context['add_url'] = reverse_lazy('add_catalogue')

        return context


class CatalogueDetailView(DetailView):
    model = Catalogue


class CatalogueCreateView(CreateView):
    model = Catalogue
    template_name = 'generic_form.html'
    form_class = CatalogueModelForm
    success_url = reverse_lazy('catalogues')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "catalogue"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class CatalogueUpdateView(UpdateView):
    model = Catalogue
    template_name = 'generic_form.html'
    form_class = CatalogueModelForm
    success_url = reverse_lazy('catalogues')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "catalogue"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class CatalogueDeleteView(DeleteView):
    model = Catalogue
    success_url = reverse_lazy('catalogues')


# CatalogueHeldBy views
class CatalogueHeldByTableView(ListView):
    model = CatalogueHeldBy
    template_name = 'generic_list.html'

    def get_queryset(self):
        return CatalogueHeldBy.objects.all()

    def get_context_data(self, **kwargs):
        context = super(CatalogueHeldByTableView, self).get_context_data(**kwargs)
        filter = CatalogueHeldByFilter(self.request.GET, queryset=self.get_queryset())

        table = CatalogueHeldByTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "catalogueheldby"
        context['add_url'] = reverse_lazy('add_catalogueheldby')

        return context


class CatalogueHeldByDetailView(DetailView):
    model = CatalogueHeldBy


class CatalogueHeldByCreateView(CreateView):
    model = CatalogueHeldBy
    template_name = 'generic_form.html'
    form_class = CatalogueHeldByModelForm
    success_url = reverse_lazy('catalogueheldbys')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "catalogueheldby"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class CatalogueHeldByUpdateView(UpdateView):
    model = CatalogueHeldBy
    template_name = 'generic_form.html'
    form_class = CatalogueHeldByModelForm
    success_url = reverse_lazy('catalogueheldbys')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "catalogueheldby"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class CatalogueHeldByDeleteView(DeleteView):
    model = CatalogueHeldBy
    success_url = reverse_lazy('catalogueheldbys')


# CatalogueType views
class CatalogueTypeTableView(ListView):
    model = CatalogueType
    template_name = 'generic_list.html'

    def get_queryset(self):
        return CatalogueType.objects.all()

    def get_context_data(self, **kwargs):
        context = super(CatalogueTypeTableView, self).get_context_data(**kwargs)
        filter = CatalogueTypeFilter(self.request.GET, queryset=self.get_queryset())

        table = CatalogueTypeTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "cataloguetype"
        context['add_url'] = reverse_lazy('add_cataloguetype')

        return context


class CatalogueTypeDetailView(DetailView):
    model = CatalogueType


class CatalogueTypeCreateView(CreateView):
    model = CatalogueType
    template_name = 'generic_form.html'
    form_class = CatalogueTypeModelForm
    success_url = reverse_lazy('cataloguetypes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "cataloguetype"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class CatalogueTypeUpdateView(UpdateView):
    model = CatalogueType
    template_name = 'generic_form.html'
    form_class = CatalogueTypeModelForm
    success_url = reverse_lazy('cataloguetypes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "cataloguetype"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class CatalogueTypeDeleteView(DeleteView):
    model = CatalogueType
    success_url = reverse_lazy('cataloguetypes')


# Collection views
class CollectionTableView(ListView):
    model = Collection
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Collection.objects.all()

    def get_context_data(self, **kwargs):
        context = super(CollectionTableView, self).get_context_data(**kwargs)
        filter = CollectionFilter(self.request.GET, queryset=self.get_queryset())

        table = CollectionTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "collection"
        context['add_url'] = reverse_lazy('add_collection')

        return context


class CollectionDetailView(DetailView):
    model = Collection


class CollectionCreateView(CreateView):
    model = Collection
    template_name = 'generic_form.html'
    form_class = CollectionModelForm
    success_url = reverse_lazy('collections')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "collection"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class CollectionUpdateView(UpdateView):
    model = Collection
    template_name = 'generic_form.html'
    form_class = CollectionModelForm
    success_url = reverse_lazy('collections')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "collection"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class CollectionDeleteView(DeleteView):
    model = Collection
    success_url = reverse_lazy('collections')


# CollectionYear views
class CollectionYearTableView(ListView):
    model = CollectionYear
    template_name = 'generic_list.html'

    def get_queryset(self):
        return CollectionYear.objects.all()

    def get_context_data(self, **kwargs):
        context = super(CollectionYearTableView, self).get_context_data(**kwargs)
        filter = CollectionYearFilter(self.request.GET, queryset=self.get_queryset())

        table = CollectionYearTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "collectionyear"
        context['add_url'] = reverse_lazy('add_collectionyear')

        return context


class CollectionYearDetailView(DetailView):
    model = CollectionYear


class CollectionYearCreateView(CreateView):
    model = CollectionYear
    template_name = 'generic_form.html'
    form_class = CollectionYearModelForm
    success_url = reverse_lazy('collectionyears')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "collectionyear"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class CollectionYearUpdateView(UpdateView):
    model = CollectionYear
    template_name = 'generic_form.html'
    form_class = CollectionYearModelForm
    success_url = reverse_lazy('collectionyears')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "collectionyear"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class CollectionYearDeleteView(DeleteView):
    model = CollectionYear
    success_url = reverse_lazy('collectionyears')


# Library views
class LibraryTableView(ListView):
    model = Library
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Library.objects.all()

    def get_context_data(self, **kwargs):
        context = super(LibraryTableView, self).get_context_data(**kwargs)
        filter = LibraryFilter(self.request.GET, queryset=self.get_queryset())

        table = LibraryTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "library"
        context['object_name_plural'] = self.model._meta.verbose_name_plural
        context['add_url'] = reverse_lazy('add_library')

        return context


class LibraryDetailView(DetailView):
    model = Library


class LibraryCreateView(CreateView):
    model = Library
    template_name = 'generic_form.html'
    form_class = LibraryModelForm
    success_url = reverse_lazy('libraries')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "library"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class LibraryUpdateView(UpdateView):
    model = Library
    template_name = 'generic_form.html'
    form_class = LibraryModelForm
    success_url = reverse_lazy('libraries')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "library"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class LibraryDeleteView(DeleteView):
    model = Library
    success_url = reverse_lazy('libraries')


# Lot views
class LotTableView(ListView):
    model = Lot
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Lot.objects.all()

    def get_context_data(self, **kwargs):
        context = super(LotTableView, self).get_context_data(**kwargs)
        filter = LotFilter(self.request.GET, queryset=self.get_queryset())

        table = LotTable(filter.qs)
        django_tables2.RequestConfig(self.request, paginate={'per_page': 10}).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "lot"
        context['add_url'] = reverse_lazy('add_lot')

        return context


class LotDetailView(DetailView):
    model = Lot


class LotCreateView(CreateView):
    model = Lot
    template_name = 'generic_form.html'
    form_class = LotModelForm
    success_url = reverse_lazy('lots')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "lot"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class LotUpdateView(UpdateView):
    model = Lot
    template_name = 'generic_form.html'
    form_class = LotModelForm
    success_url = reverse_lazy('lots')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "lot"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class LotDeleteView(DeleteView):
    model = Lot
    success_url = reverse_lazy('lots')


# PersonCatalogueRelation views
class PersonCatalogueRelationTableView(ListView):
    model = PersonCatalogueRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return PersonCatalogueRelation.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PersonCatalogueRelationTableView, self).get_context_data(**kwargs)
        filter = PersonCatalogueRelationFilter(self.request.GET, queryset=self.get_queryset())

        table = PersonCatalogueRelationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "personcataloguerelation"
        context['add_url'] = reverse_lazy('add_personcataloguerelation')

        return context


class PersonCatalogueRelationDetailView(DetailView):
    model = PersonCatalogueRelation


class PersonCatalogueRelationCreateView(CreateView):
    model = PersonCatalogueRelation
    template_name = 'generic_form.html'
    form_class = PersonCatalogueRelationModelForm
    success_url = reverse_lazy('personcataloguerelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "personcataloguerelation"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class PersonCatalogueRelationUpdateView(UpdateView):
    model = PersonCatalogueRelation
    template_name = 'generic_form.html'
    form_class = PersonCatalogueRelationModelForm
    success_url = reverse_lazy('personcataloguerelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "personcataloguerelation"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class PersonCatalogueRelationDeleteView(DeleteView):
    model = PersonCatalogueRelation
    success_url = reverse_lazy('personcataloguerelations')


# PersonCatalogueRelationRole views
class PersonCatalogueRelationRoleTableView(ListView):
    model = PersonCatalogueRelationRole
    template_name = 'generic_list.html'

    def get_queryset(self):
        return PersonCatalogueRelationRole.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PersonCatalogueRelationRoleTableView, self).get_context_data(**kwargs)
        filter = PersonCatalogueRelationRoleFilter(self.request.GET, queryset=self.get_queryset())

        table = PersonCatalogueRelationRoleTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "personcataloguerelationrole"
        context['add_url'] = reverse_lazy('add_personcataloguerelationrole')

        return context


class PersonCatalogueRelationRoleDetailView(DetailView):
    model = PersonCatalogueRelationRole


class PersonCatalogueRelationRoleCreateView(CreateView):
    model = PersonCatalogueRelationRole
    template_name = 'generic_form.html'
    form_class = PersonCatalogueRelationRoleModelForm
    success_url = reverse_lazy('personcataloguerelationroles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "personcataloguerelationrole"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class PersonCatalogueRelationRoleUpdateView(UpdateView):
    model = PersonCatalogueRelationRole
    template_name = 'generic_form.html'
    form_class = PersonCatalogueRelationRoleModelForm
    success_url = reverse_lazy('personcataloguerelationroles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "personcataloguerelationrole"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class PersonCatalogueRelationRoleDeleteView(DeleteView):
    model = PersonCatalogueRelationRole
    success_url = reverse_lazy('personcataloguerelationroles')


# PersonCollectionRelation views
class PersonCollectionRelationTableView(ListView):
    model = PersonCollectionRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return PersonCollectionRelation.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PersonCollectionRelationTableView, self).get_context_data(**kwargs)
        filter = PersonCollectionRelationFilter(self.request.GET, queryset=self.get_queryset())

        table = PersonCollectionRelationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "personcollectionrelation"
        context['add_url'] = reverse_lazy('add_personcollectionrelation')

        return context


class PersonCollectionRelationDetailView(DetailView):
    model = PersonCollectionRelation


class PersonCollectionRelationCreateView(CreateView):
    model = PersonCollectionRelation
    template_name = 'generic_form.html'
    form_class = PersonCollectionRelationModelForm
    success_url = reverse_lazy('personcollectionrelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "personcollectionrelation"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class PersonCollectionRelationUpdateView(UpdateView):
    model = PersonCollectionRelation
    template_name = 'generic_form.html'
    form_class = PersonCollectionRelationModelForm
    success_url = reverse_lazy('personcollectionrelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "personcollectionrelation"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class PersonCollectionRelationDeleteView(DeleteView):
    model = PersonCollectionRelation
    success_url = reverse_lazy('personcollectionrelations')


