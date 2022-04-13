from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.db.models import Count, Min, Max, Q
from django.db.models.functions import Substr, Length
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist

from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import get_objects_for_user

from mediate.tools import put_layout_in_context, put_get_variable_in_context
from mediate.views import GenericDetailView
from simplemoderation.tools import moderate

from ..forms import *
from ..tables import *
from ..filters import *

from ..models import *
from catalogues.tools import get_datasets_for_session, get_dataset_for_anonymoususer

from items.models import Item, Edition
import json

import django_tables2


def get_catalogues_for_session(request, extra_catalogue=None):
    return Collection.objects.filter(
        Q(collection_tmp__dataset__in=get_datasets_for_session(request))
        | Q(pk=extra_catalogue.pk if extra_catalogue else None)
    )


# Catalogue views
class CatalogueTableView(ListView):
    model = Collection
    template_name = 'catalogue_list.html'

    def get_queryset(self):
        return get_catalogues_for_session(self.request).distinct()

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

        # Extra data, used for e.g. charts
        max_publication_year = get_catalogues_for_session(self.request).aggregate(Max('lot__catalogue__year_of_publication'))['lot__catalogue__year_of_publication__max']
        if not max_publication_year:
            max_publication_year = 0
        context['max_publication_year'] = max_publication_year

        item_count_per_decade = Item.objects\
            .filter(lot__catalogue__in=filter.qs, edition__year_start__lte=max_publication_year)\
            .annotate(decade=10 * Substr('edition__year_start', 1, Length('edition__year_start') - 1))\
            .values('decade')\
            .order_by('decade')\
            .annotate(count=Count('decade'))
        extra_data = {
            'item_count_per_decade': list(item_count_per_decade)
        }
        context['extra_data'] = json.dumps(extra_data)

        item_count_total = Item.objects.filter(lot__catalogue__in=filter.qs).count()
        context['item_count_total'] = item_count_total
        item_count_without_year = Item.objects.filter(lot__catalogue__in=filter.qs, edition__year_start__isnull=True).count()
        context['item_count_without_year'] = item_count_without_year
        item_count_in_plot = Item.objects.filter(lot__catalogue__in=filter.qs, edition__year_start__lte=max_publication_year).count()
        context['item_count_in_plot'] = item_count_in_plot
        context['item_percentage_in_plot'] = int(100 * item_count_in_plot / item_count_total) if item_count_total != 0 else 0

        context['map_url'] = reverse_lazy('cataloguesmap')

        context['per_page_choices'] = [10, 25, 50, 100]

        return context


class CatalogueLocationMapView(ListView):
    model = Collection
    template_name = 'generic_location_map.html'

    def get_queryset(self):
        catalogues = get_catalogues_for_session(self.request).filter(related_places__place__latitude__isnull=False,
                                                                     related_places__place__longitude__isnull=False)
        return catalogues

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        context = super(CatalogueLocationMapView, self).get_context_data(**kwargs)
        filter = CatalogueFilter(self.request.GET, queryset=queryset)

        context['filter'] = filter
        context['object_name'] = "catalogue"

        context['object_list'] = filter.qs
        context['places'] = Place.objects.filter(related_catalogues__catalogue__in=filter.qs)\
                                .annotate(object_count=Count('related_catalogues__catalogue'))
        context['objects_url_name'] = 'catalogues'
        context['place_search_field'] = 'place'

        return context


class CatalogueDetailView(PermissionRequiredMixin, DetailView):
    model = Collection

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection_tmp.dataset
    # End permission check

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)

        # Find the first lot for each page
        context['first_lot_on_page_dict'] = dict([
            (lot['first_lot_on_page'], lot['page_in_catalogue']) for lot in
            self.object.lot_set.filter(page_in_catalogue__isnull=False).values('page_in_catalogue')
                .annotate(first_lot_on_page=Min('index_in_catalogue')).order_by()
        ])

        # Find the first lot for each category
        # by looping over the ordered lots in the catalogue
        lots = self.object.lot_set.filter(category__isnull=False).values(
            'index_in_catalogue', 'category__bookseller_category', 'number_in_catalogue').order_by('index_in_catalogue')
        first_lot_in_category_dict = {}
        last_category = ""
        for lot in lots:
            if lot['category__bookseller_category'] != last_category or lot['number_in_catalogue'] == 1:
                last_category = lot['category__bookseller_category']
                first_lot_in_category_dict[lot['index_in_catalogue']] = lot['category__bookseller_category']
        context['first_lot_in_category_dict'] = first_lot_in_category_dict

        return context


class CatalogueDetailBareView(CatalogueDetailView):
    template_name = 'catalogues/catalogue_detail_bare.html'


@moderate()
class CatalogueCreateView(CreateView):
    model = Collection
    template_name = 'generic_form.html'
    form_class = CatalogueModelForm
    success_url = reverse_lazy('catalogues')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['datasets'] = get_datasets_for_session(self.request)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "catalogue"
        return context


@moderate()
class CatalogueUpdateView(PermissionRequiredMixin, UpdateView):
    model = Collection
    template_name = 'generic_form.html'
    form_class = CatalogueModelForm

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().collection_tmp.dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        catalogue = self.get_object()
        kwargs['datasets'] = get_datasets_for_session(
            self.request,
            catalogue.collection_tmp.dataset
        )
        if catalogue.collection_tmp.dataset not in get_datasets_for_session(self.request):
            messages.warning(self.request,
                             format_html(_("The dataset this Catalogue belongs to, <i>{}</i>, is "
                                           "currently not selected."),
                                         catalogue.collection_tmp.dataset))

        return kwargs

    def get(self, request, *args, **kwargs):
        # Check whether the user has permission to view this catalogue
        if not self.request.user.has_perm('catalogues.change_dataset', self.get_object().collection_tmp.dataset):
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.GET.get('next') or reverse_lazy('catalogues')

    @put_get_variable_in_context([('next', 'next_url'),])
    @put_layout_in_context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "catalogue"
        return context


@moderate()
class CatalogueDeleteView(PermissionRequiredMixin, DeleteView):
    model = Collection
    success_url = reverse_lazy('catalogues')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().collection_tmp.dataset
    # End permission check

    def get(self, request, *args, **kwargs):
        # Check whether the user has permission to view this catalogue
        if not self.request.user.has_perm('catalogues.change_dataset', self.get_object().collection_tmp.dataset):
            raise PermissionDenied
        return super().get(request, *args, **kwargs)


# CatalogueHeldBy views
class CatalogueHeldByTableView(ListView):
    model = CollectionHeldBy
    template_name = 'generic_list.html'

    def get_queryset(self):
        return CollectionHeldBy.objects.filter(catalogue__collection_tmp__dataset__in=get_datasets_for_session(self.request))

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


class CatalogueHeldByDetailView(PermissionRequiredMixin, DetailView):
    model = CollectionHeldBy
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection.collection_tmp.dataset
    # End permission check


class CatalogueHeldByCreateView(CreateView):
    model = CollectionHeldBy
    template_name = 'generic_form.html'
    form_class = CatalogueHeldByModelForm
    success_url = reverse_lazy('catalogueheldbys')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "catalogueheldby"
        return context


class CatalogueHeldByUpdateView(UpdateView):
    model = CollectionHeldBy
    template_name = 'generic_form.html'
    form_class = CatalogueHeldByModelForm
    success_url = reverse_lazy('catalogueheldbys')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "catalogueheldby"
        return context


class CatalogueHeldByDeleteView(DeleteView):
    model = CollectionHeldBy
    success_url = reverse_lazy('catalogueheldbys')


# CatalogueType views
class CatalogueTypeTableView(ListView):
    model = CollectionType
    template_name = 'generic_list.html'

    def get_queryset(self):
        return CollectionType.objects.all()

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
    model = CollectionType


class CatalogueTypeCreateView(CreateView):
    model = CollectionType
    template_name = 'generic_form.html'
    form_class = CatalogueTypeModelForm
    success_url = reverse_lazy('cataloguetypes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "cataloguetype"
        return context


class CatalogueTypeUpdateView(UpdateView):
    model = CollectionType
    template_name = 'generic_form.html'
    form_class = CatalogueTypeModelForm
    success_url = reverse_lazy('cataloguetypes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "cataloguetype"
        return context


class CatalogueTypeDeleteView(DeleteView):
    model = CollectionType
    success_url = reverse_lazy('cataloguetypes')


# CatalogueCatalogueTypeRelation views
class CatalogueCatalogueTypeRelationTableView(ListView):
    model = CollectionCollectionTypeRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return CollectionCollectionTypeRelation.objects\
            .filter(catalogue__collection_tmp__dataset__in=get_datasets_for_session(self.request))

    def get_context_data(self, **kwargs):
        context = super(CatalogueCatalogueTypeRelationTableView, self).get_context_data(**kwargs)
        filter = CatalogueCatalogueTypeRelationFilter(self.request.GET, queryset=self.get_queryset())

        table = CatalogueCatalogueTypeRelationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "cataloguecataloguetyperelation"
        context['add_url'] = reverse_lazy('add_cataloguecataloguetyperelation')

        return context


class CatalogueCatalogueTypeRelationDetailView(PermissionRequiredMixin, DetailView):
    model = CollectionCollectionTypeRelation
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection.collection_tmp.dataset
    # End permission check


class CatalogueCatalogueTypeRelationCreateView(CreateView):
    model = CollectionCollectionTypeRelation
    template_name = 'generic_form.html'
    form_class = CatalogueCatalogueTypeRelationModelForm
    success_url = reverse_lazy('cataloguecataloguetyperelations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['catalogues'] = get_catalogues_for_session(self.request)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "cataloguecataloguetyperelation"
        return context


class CatalogueCatalogueTypeRelationUpdateView(PermissionRequiredMixin, UpdateView):
    model = CollectionCollectionTypeRelation
    template_name = 'generic_form.html'
    form_class = CatalogueCatalogueTypeRelationModelForm
    success_url = reverse_lazy('cataloguecataloguetyperelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().collection.collection_tmp.dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        relation = self.get_object()
        kwargs['catalogues'] = get_catalogues_for_session(
            self.request,
            relation.collection
        )
        if relation.collection.collection_tmp.dataset not in get_datasets_for_session(self.request):
            messages.warning(self.request,
                             format_html(_("The dataset this CatalogueCatalogueTypeRelation belongs to, <i>{}</i>, is "
                                           "currently not selected."),
                                         relation.collection.collection_tmp.dataset))

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "cataloguecataloguetyperelation"
        return context


class CatalogueCatalogueTypeRelationDeleteView(PermissionRequiredMixin, DeleteView):
    model = CollectionCollectionTypeRelation
    success_url = reverse_lazy('cataloguecataloguetyperelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().collection.collection_tmp.dataset
    # End permission check


# Collection_TMP views
class Collection_TMPTableView(ListView):
    model = Collection_TMP
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Collection_TMP.objects.filter(dataset__in=get_datasets_for_session(self.request))

    def get_context_data(self, **kwargs):
        context = super(Collection_TMPTableView, self).get_context_data(**kwargs)
        filter = Collection_TMPFilter(self.request.GET, queryset=self.get_queryset())

        table = Collection_TMPTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "collection_tmp"
        context['add_url'] = reverse_lazy('add_collection_tmp')

        return context


class Collection_TMPDetailView(PermissionRequiredMixin, GenericDetailView):
    model = Collection_TMP
    object_fields = ['name', 'dataset']
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().dataset
    # End permission check


class Collection_TMPCreateView(CreateView):
    model = Collection_TMP
    template_name = 'generic_form.html'
    form_class = Collection_TMPModelForm
    success_url = reverse_lazy('collection_tmps')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['datasets'] = get_objects_for_user(self.request.user, 'catalogues.change_dataset') \
                             or get_dataset_for_anonymoususer()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "collection_tmp"
        return context


class Collection_TMPUpdateView(PermissionRequiredMixin, UpdateView):
    model = Collection_TMP
    template_name = 'generic_form.html'
    form_class = Collection_TMPModelForm
    success_url = reverse_lazy('collection_tmps')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['datasets'] = get_objects_for_user(self.request.user, 'catalogues.change_dataset') \
                             or get_dataset_for_anonymoususer()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "collection_tmp"
        return context


class Collection_TMPDeleteView(PermissionRequiredMixin, DeleteView):
    model = Collection_TMP
    success_url = reverse_lazy('collection_tmps')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().dataset
    # End permission check


# Collection_TMPYear views
class Collection_TMPYearTableView(ListView):
    model = Collection_TMPYear
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Collection_TMPYear.objects.all()

    def get_context_data(self, **kwargs):
        context = super(Collection_TMPYearTableView, self).get_context_data(**kwargs)
        filter = Collection_TMPYearFilter(self.request.GET, queryset=self.get_queryset())

        table = Collection_TMPYearTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "collection_tmpyear"
        context['add_url'] = reverse_lazy('add_collection_tmpyear')

        return context


class Collection_TMPYearDetailView(DetailView):
    model = Collection_TMPYear


class Collection_TMPYearCreateView(CreateView):
    model = Collection_TMPYear
    template_name = 'generic_form.html'
    form_class = Collection_TMPYearModelForm
    success_url = reverse_lazy('collection_tmpyears')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "collection_tmpyear"
        return context


class Collection_TMPYearUpdateView(UpdateView):
    model = Collection_TMPYear
    template_name = 'generic_form.html'
    form_class = Collection_TMPYearModelForm
    success_url = reverse_lazy('collection_tmpyears')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "collection_tmpyear"
        return context


class Collection_TMPYearDeleteView(DeleteView):
    model = Collection_TMPYear
    success_url = reverse_lazy('collection_tmpyears')


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


class LibraryDeleteView(DeleteView):
    model = Library
    success_url = reverse_lazy('libraries')


# Lot views
class LotTableView(ListView):
    model = Lot
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Lot.objects.filter(catalogue__collection_tmp__dataset__in=get_datasets_for_session(self.request))\
            .order_by('catalogue__year_of_publication', 'catalogue__short_title', 'index_in_catalogue',
                                    'lot_as_listed_in_catalogue')

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


class LotDetailView(PermissionRequiredMixin, GenericDetailView):
    model = Lot
    object_fields = ['catalogue', 'number_in_catalogue', 'page_in_catalogue', 'sales_price',
                     'lot_as_listed_in_catalogue', 'index_in_catalogue', 'category']

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection.collection_tmp.dataset
    # End permission check


@moderate()
class LotCreateView(CreateView):
    model = Lot
    template_name = 'generic_form.html'
    form_class = LotModelForm
    success_url = reverse_lazy('lots')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['catalogues'] = get_catalogues_for_session(self.request)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "lot"
        return context


@moderate()
class LotUpdateView(PermissionRequiredMixin, UpdateView):
    model = Lot
    template_name = 'generic_form.html'
    form_class = LotModelForm

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().collection.collection_tmp.dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        lot = self.get_object()
        kwargs['catalogues'] = get_catalogues_for_session(
            self.request,
            lot.collection
        )
        if lot.collection.collection_tmp.dataset not in get_datasets_for_session(self.request):
            messages.warning(self.request,
                             format_html(_("The dataset this Lot belongs to, <i>{}</i>, is "
                                           "currently not selected."),
                                         lot.collection.collection_tmp.dataset))
        return kwargs

    def get_success_url(self):
        return self.request.GET.get('next') or reverse_lazy('lots')

    @put_layout_in_context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "lot"
        if 'next' in self.request.GET:
            context['next_url'] = '{}#lot__{}'.format(self.request.GET['next'], self.get_object().uuid)
        return context


@moderate()
class LotDeleteView(PermissionRequiredMixin, DeleteView):
    model = Lot
    success_url = reverse_lazy('lots')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().collection.collection_tmp.dataset
    # End permission check


def previous_lot_view(request, pk, index):
    try:
        lot = Lot.objects.get(catalogue__uuid=pk, index_in_catalogue=index)
        if not request.user.has_perm('catalogues.view_dataset', lot.collection.collection_tmp.dataset):
            raise PermissionDenied()
        return JsonResponse({
            'success': True,
            'lot_as_listed_in_catalogue': lot.lot_as_listed_in_collection,
            'index_in_catalogue': lot.index_in_collection
        })
    except ObjectDoesNotExist:
        return JsonResponse({
            'success': False
        })


def expand_lot_view(request, pk):
    lot = get_object_or_404(Lot, pk=pk)
    if not request.user.has_perm('catalogues.view_dataset', lot.collection.collection_tmp.dataset):
        raise PermissionDenied()
    next_url = reverse_lazy('catalogue_detail_bare', args=[str(lot.collection.uuid)])

    if request.method == 'POST':
        next_url = '{}#lot__{}'.format(next_url, lot.uuid)
        form = LotExpandForm(request.POST)
        if form.is_valid():
            number = int(form.cleaned_data.get('number', 0))
            prefix = form.cleaned_data.get('prefix', '')
            last_item_index = Item.objects.filter(lot=lot).aggregate(Max('index_in_lot')).get('index_in_lot__max')
            print("last_item_index", last_item_index)
            for index in range(2, number + 1):
                edition = Edition.objects.create()

                index_in_lot = last_item_index + index - 1
                short_title = "{} [{} of {}]".format(prefix, index, number)
                item = Item.objects.create(short_title=short_title, lot=lot, index_in_lot=index_in_lot,
                                           collection_tmp=lot.collection.collection_tmp, edition=edition)
        return HttpResponseRedirect(next_url)
    elif request.method == 'GET':
        next_url = request.GET.get('next', next_url)

    context = {
        'form': LotExpandForm(),
        'extended_layout': 'barelayout.html',
        'action': _("Expand"),
        'object_name': "lot: {}".format(lot.lot_as_listed_in_collection),
        'next_url': next_url
    }
    return render(request, 'generic_form.html', context=context)


def add_lot_before(request, pk):
    """
    Add a lot at a certain position in the list of lots of a catalogue.
    The position is determined as *before* the lot with 'pk' as the id.
    If the 'page' url parameter is set, it means the page before the page of the selected lot.
    If the 'category' url parameter is set, it means the category before the category of the selected lot.
    :param request: 
    :param pk: 
    :return: 
    """
    lot_after = get_object_or_404(Lot, pk=pk)
    if not request.user.has_perm('catalogues.view_dataset', lot_after.collection.collection_tmp.dataset):
        raise PermissionDenied()

    # Determine whether there is a lot before the selected position
    try:
        lot_before = Lot.objects.filter(catalogue=lot_after.collection, index_in_catalogue__lt=lot_after.index_in_collection)\
            .order_by('-index_in_catalogue').first()
    except:
        lot_before = None

    next_url = reverse_lazy('catalogue_detail_bare', args=[str(lot_after.collection.uuid)])
    next_url = '{}#lot__{}'.format(next_url, lot_after.uuid)

    if request.method == 'POST':
        form = AddLotBeforeForm(request.POST)
        if form.is_valid():
            new_lot = form.save()

            # Create Item for this new Lot
            empty_edition = Edition.objects.create()
            Item.objects.create(
                lot=new_lot,
                edition=empty_edition,
                short_title=new_lot.lot_as_listed_in_collection[:128],
                index_in_lot=1
            )

            return HttpResponseRedirect(next_url)
    elif request.method == 'GET':
        if 'category' in request.GET:
            if lot_before:
                category = lot_before.category
            else:
                category = None
        else:
            category = lot_after.category

        if 'page' in request.GET:
            if lot_before:
                page = lot_before.page_in_catalogue
            elif lot_after.page_in_collection > 1:
                page = lot_after.page_in_collection - 1
            else:
                page = lot_after.page_in_collection
        else:
            page = lot_after.page_in_collection

        index = lot_after.index_in_collection

        form = AddLotBeforeForm(category=category, page=page, index=index, catalogue=lot_after.collection)
    else:
        form = AddLotBeforeForm()

    context = {
        'form': form,
        'extended_layout': 'barelayout.html',
        'action': _("Add lot"),
        'next_url': next_url
    }

    return render(request, 'generic_form.html', context=context)


def add_lot_at_end(request, pk):
    """
    Add a lot at the end of a catalogue
    :param request:
    :param pk:
    :return:
    """
    catalogue = get_object_or_404(Collection, pk=pk)
    if request.user.has_perm('catalogues.view_dataset', catalogue.collection_tmp.dataset):
        raise PermissionDenied()
    last_lot = Lot.objects.filter(catalogue=catalogue).order_by('-index_in_catalogue').first()

    next_url = reverse_lazy('catalogue_detail_bare', args=[str(catalogue.uuid)])
    next_url = '{}#lot__{}'.format(next_url, last_lot.uuid)

    if request.method == 'POST':
        form = AddLotAtEndForm(request.POST)
        if form.is_valid():
            new_lot = form.save()

            # Create Item for this new Lot
            empty_edition = Edition.objects.create()
            Item.objects.create(
                lot=new_lot,
                edition=empty_edition,
                short_title=new_lot.lot_as_listed_in_collection[:128],
                index_in_lot=1
            )

            return HttpResponseRedirect(next_url)
    elif request.method == 'GET':
        category = last_lot.category
        page = last_lot.page_in_collection
        index = last_lot.index_in_collection + 1
        form = AddLotAtEndForm(category=category, page=page, index=index, catalogue=catalogue)
    else:
        form = AddLotAtEndForm()

    context = {
        'form': form,
        'extended_layout': 'barelayout.html',
        'action': _("Add lot"),
        'next_url': next_url
    }

    return render(request, 'generic_form.html', context=context)


# PersonCatalogueRelation views
class PersonCatalogueRelationTableView(ListView):
    model = PersonCollectionRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return PersonCollectionRelation.objects.filter(
            catalogue__collection_tmp__dataset__in=get_datasets_for_session(self.request)
        )

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


class PersonCatalogueRelationDetailView(PermissionRequiredMixin, DetailView):
    model = PersonCollectionRelation
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection.collection_tmp.dataset
    # End permission check


class PersonCatalogueRelationCreateView(CreateView):
    model = PersonCollectionRelation
    template_name = 'generic_form.html'
    form_class = PersonCatalogueRelationModelForm
    success_url = reverse_lazy('personcataloguerelations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['catalogues'] = get_catalogues_for_session(self.request)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "personcataloguerelation"
        return context


class PersonCatalogueRelationUpdateView(PermissionRequiredMixin, UpdateView):
    model = PersonCollectionRelation
    template_name = 'generic_form.html'
    form_class = PersonCatalogueRelationModelForm
    success_url = reverse_lazy('personcataloguerelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection.collection_tmp.dataset

    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        personcataloguerelation = self.get_object()
        kwargs['catalogues'] = get_catalogues_for_session(
            self.request,
            personcataloguerelation.collection
        )
        if personcataloguerelation.collection.collection_tmp.dataset not in get_datasets_for_session(self.request):
            messages.warning(self.request,
                             format_html(_("The dataset this PersonCatalogueRelation belongs to, <i>{}</i>, is "
                                           "currently not selected."),
                                         personcataloguerelation.collection.collection_tmp.dataset))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "personcataloguerelation"
        return context


class PersonCatalogueRelationDeleteView(PermissionRequiredMixin, DeleteView):
    model = PersonCollectionRelation
    success_url = reverse_lazy('personcataloguerelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection.collection_tmp.dataset
    # End permission check


# PersonCatalogueRelationRole views
class PersonCatalogueRelationRoleTableView(ListView):
    model = PersonCollectionRelationRole
    template_name = 'generic_list.html'

    def get_queryset(self):
        return PersonCollectionRelationRole.objects.all()

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
    model = PersonCollectionRelationRole


class PersonCatalogueRelationRoleCreateView(CreateView):
    model = PersonCollectionRelationRole
    template_name = 'generic_form.html'
    form_class = PersonCatalogueRelationRoleModelForm
    success_url = reverse_lazy('personcataloguerelationroles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "personcataloguerelationrole"
        return context


class PersonCatalogueRelationRoleUpdateView(UpdateView):
    model = PersonCollectionRelationRole
    template_name = 'generic_form.html'
    form_class = PersonCatalogueRelationRoleModelForm
    success_url = reverse_lazy('personcataloguerelationroles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "personcataloguerelationrole"
        return context


class PersonCatalogueRelationRoleDeleteView(DeleteView):
    model = PersonCollectionRelationRole
    success_url = reverse_lazy('personcataloguerelationroles')


# PersonCollection_TMPRelation views
class PersonCollection_TMPRelationTableView(ListView):
    model = PersonCollection_TMPRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return PersonCollection_TMPRelation.objects.filter(collection_tmp__dataset__in=get_datasets_for_session(self.request))

    def get_context_data(self, **kwargs):
        context = super(PersonCollection_TMPRelationTableView, self).get_context_data(**kwargs)
        filter = PersonCollection_TMPRelationFilter(self.request.GET, queryset=self.get_queryset())

        table = PersonCollection_TMPRelationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "personcollection_tmprelation"
        context['add_url'] = reverse_lazy('add_personcollection_tmprelation')

        return context


class PersonCollection_TMPRelationDetailView(PermissionRequiredMixin, DetailView):
    model = PersonCollection_TMPRelation
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection_tmp.dataset
    # End permission check


class PersonCollection_TMPRelationCreateView(CreateView):
    model = PersonCollection_TMPRelation
    template_name = 'generic_form.html'
    form_class = PersonCollection_TMPRelationModelForm
    success_url = reverse_lazy('personcollection_tmprelations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['collection_tmps'] = Collection_TMP.objects.filter(dataset__in=get_datasets_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "personcollection_tmprelation"
        return context


class PersonCollection_TMPRelationUpdateView(PermissionRequiredMixin, UpdateView):
    model = PersonCollection_TMPRelation
    template_name = 'generic_form.html'
    form_class = PersonCollection_TMPRelationModelForm
    success_url = reverse_lazy('personcollection_tmprelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().collection_tmp.dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        personcollection_tmprelation = self.get_object()
        kwargs['collection_tmps'] = Collection_TMP.objects.filter(
            Q(dataset__in=get_datasets_for_session(self.request))
            | Q(uuid=personcollection_tmprelation.collection_tmp.uuid)
        )
        if personcollection_tmprelation.collection_tmp.dataset not in get_datasets_for_session(self.request):
            messages.warning(self.request,
                             format_html(_("The dataset this PersonCollection_TMPRelation belongs to, <i>{}</i>, is "
                                           "currently not selected."),
                                         personcollection_tmprelation.collection_tmp.dataset))

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "personcollection_tmprelation"
        return context


class PersonCollection_TMPRelationDeleteView(PermissionRequiredMixin, DeleteView):
    model = PersonCollection_TMPRelation
    success_url = reverse_lazy('personcollection_tmprelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().collection_tmp.dataset
    # End permission check


class CataloguePlaceRelationTableView(ListView):
    model = CollectionPlaceRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return CollectionPlaceRelation.objects\
            .filter(catalogue__collection_tmp__dataset__in=get_datasets_for_session(self.request))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter = CataloguePlaceRelationFilter(self.request.GET, queryset=self.get_queryset())

        table = CataloguePlaceRelationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name_plural'] = self.model._meta.verbose_name_plural
        context['add_url'] = reverse_lazy('add_catalogueplacerelation')

        return context


class CataloguePlaceRelationDetailView(PermissionRequiredMixin, DetailView):
    model = CollectionPlaceRelation
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection.collection_tmp.dataset
    # End permission check


class CataloguePlaceRelationCreateView(CreateView):
    model = CollectionPlaceRelation
    template_name = 'generic_form.html'
    form_class = CataloguePlaceRelationModelForm
    success_url = reverse_lazy('catalogueplacerelations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['catalogues'] = get_catalogues_for_session(self.request)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "catalogue publication place"
        return context


class CataloguePlaceRelationUpdateView(PermissionRequiredMixin, UpdateView):
    model = CollectionPlaceRelation
    template_name = 'generic_form.html'
    form_class = CataloguePlaceRelationModelForm
    success_url = reverse_lazy('catalogueplacerelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().collection.collection_tmp.dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        relation = self.get_object()
        kwargs['catalogues'] = get_catalogues_for_session(
            self.request,
            relation.collection
        )
        if relation.collection.collection_tmp.dataset not in get_datasets_for_session(self.request):
            messages.warning(self.request,
                             format_html(_("The dataset this CataloguePlaceRelation belongs to, <i>{}</i>, is "
                                           "currently not selected."),
                                         relation.collection.collection_tmp.dataset))

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "catalogue publication place"
        return context


class CataloguePlaceRelationDeleteView(PermissionRequiredMixin, DeleteView):
    model = CollectionPlaceRelation
    success_url = reverse_lazy('catalogueplacerelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().collection.collection_tmp.dataset
    # End permission check


# Category views
class CategoryTableView(ListView):
    model = Category
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Category.objects.filter(catalogue__collection_tmp__dataset__in=get_datasets_for_session(self.request))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter = CategoryFilter(self.request.GET, queryset=self.get_queryset())

        table = CategoryTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name_plural'] = self.model._meta.verbose_name_plural
        context['add_url'] = reverse_lazy('add_category')

        return context


class CategoryDetailView(PermissionRequiredMixin, GenericDetailView):
    model = Category
    object_fields = ['catalogue', 'parent', 'bookseller_category', 'parisian_category']
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection.collection_tmp.dataset
    # End permission check


class CategoryCreateView(CreateView):
    model = Category
    template_name = 'generic_form.html'
    form_class = CategoryModelForm
    success_url = reverse_lazy('categories')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['catalogues'] = get_catalogues_for_session(self.request)
        kwargs['categories'] = Category.objects.filter(catalogue__collection_tmp__dataset__in=get_datasets_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "category"
        return context
    
    
class CategoryUpdateView(PermissionRequiredMixin, UpdateView):
    model = Category
    template_name = 'generic_form.html'
    form_class = CategoryModelForm
    success_url = reverse_lazy('categories')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().collection.collection_tmp.dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        category = self.get_object()
        kwargs['catalogues'] = get_catalogues_for_session(
            self.request,
            category.collection
        )
        kwargs['categories'] = Category.objects.filter(
            Q(catalogue__collection_tmp__dataset__in=get_datasets_for_session(self.request))
            | Q(pk=category.pk)
        )
        if category.collection.collection_tmp.dataset not in get_datasets_for_session(self.request):
            messages.warning(self.request,
                             format_html(_("The dataset this Category belongs to, <i>{}</i>, is "
                                           "currently not selected."),
                                         category.collection.collection_tmp.dataset))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "category"
        return context


class CategoryDeleteView(PermissionRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('categories')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().collection.collection_tmp.dataset
    # End permission check


# ParisianCategory views
class ParisianCategoryTableView(ListView):
    model = ParisianCategory
    template_name = 'generic_list.html'

    def get_queryset(self):
        return ParisianCategory.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter = ParisianCategoryFilter(self.request.GET, queryset=self.get_queryset())

        table = ParisianCategoryTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name_plural'] = self.model._meta.verbose_name_plural
        context['add_url'] = reverse_lazy('add_parisiancategory')

        return context


class ParisianCategoryDetailView(DetailView):
    model = ParisianCategory


class ParisianCategoryCreateView(CreateView):
    model = ParisianCategory
    template_name = 'generic_form.html'
    form_class = ParisianCategoryModelForm
    success_url = reverse_lazy('parisiancategories')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "parisiancategory"
        return context


class ParisianCategoryUpdateView(UpdateView):
    model = ParisianCategory
    template_name = 'generic_form.html'
    form_class = ParisianCategoryModelForm
    success_url = reverse_lazy('parisiancategories')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "parisiancategory"
        return context


class ParisianCategoryDeleteView(DeleteView):
    model = ParisianCategory
    success_url = reverse_lazy('parisiancategories')


# CataloguePlaceRelationType views
class CataloguePlaceRelationTypeTableView(ListView):
    model = CollectionPlaceRelationType
    template_name = 'generic_list.html'

    def get_queryset(self):
        return CollectionPlaceRelationType.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter = CataloguePlaceRelationTypeFilter(self.request.GET, queryset=self.get_queryset())

        table = CataloguePlaceRelationTypeTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name_plural'] = self.model._meta.verbose_name_plural
        context['add_url'] = reverse_lazy('add_catalogueplacerelationtype')

        return context


class CataloguePlaceRelationTypeDetailView(DetailView):
    model = CollectionPlaceRelationType


class CataloguePlaceRelationTypeCreateView(CreateView):
    model = CollectionPlaceRelationType
    template_name = 'generic_form.html'
    form_class = CataloguePlaceRelationTypeModelForm
    success_url = reverse_lazy('catalogueplacerelationtypes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "catalogueplacerelationtype"
        return context


class CataloguePlaceRelationTypeUpdateView(UpdateView):
    model = CollectionPlaceRelationType
    template_name = 'generic_form.html'
    form_class = CataloguePlaceRelationTypeModelForm
    success_url = reverse_lazy('catalogueplacerelationtypes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "catalogueplacerelationtype"
        return context


class CataloguePlaceRelationTypeDeleteView(DeleteView):
    model = CollectionPlaceRelationType
    success_url = reverse_lazy('catalogueplacerelationtypes')
