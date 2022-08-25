from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html, escape
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.db.models import Count, Min, Max, Q, Func, F, Value
from django.db.models.functions import Substr, Length
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
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
from catalogues.tools import get_datasets_for_session, get_dataset_for_anonymoususer, get_permitted_datasets_for_session

from items.models import Item, Edition, Language, BookFormat
import json
from collections import Counter

import django_tables2


def get_collections_for_session(request, extra_collection=None):
    return Collection.objects.filter(
        Q(catalogue__dataset__in=get_datasets_for_session(request))
        | Q(pk=extra_collection.pk if extra_collection else None)
    )


# Collection views
class CollectionTableView(ListView):
    model = Collection
    template_name = 'generic_list.html'

    def get_queryset(self):
        return get_collections_for_session(self.request).distinct()

    def get_context_data(self, **kwargs):
        context = super(CollectionTableView, self).get_context_data(**kwargs)
        filter = CollectionFilter(self.request.GET, queryset=self.get_queryset())

        table = CollectionTable(filter.qs)
        django_tables2.RequestConfig(self.request, paginate={'per_page': 25}).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "collection"
        if self.request.user.has_perm('catalogues.add_collection'):
            context['add_url'] = reverse_lazy('add_collection')
        context['map_url'] = reverse_lazy('collectionsmap')

        context['per_page_choices'] = [10, 25, 50, 100]

        context['url_params'] = self.request.GET.urlencode()
        context['statistics_url'] = reverse_lazy('collection_statistics')

        return context


class CollectionStatisticsView(TemplateView):
    template_name = 'generic_statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chart_url'] = reverse_lazy('get_collection_chart')
        filter = CollectionFilter(self.request.GET, queryset=get_collections_for_session(self.request).distinct())

        context['filter'] = filter
        context['object_name'] = "collection"

        context['url_params'] = self.request.GET.urlencode()

        context['charts'] = [
            [
                {
                    'id': 'collection_chart',
                    'title': _('Number of items per decade'),
                    'url': reverse_lazy('get_collection_chart')
                },
            ],
            [
                {
                    'id': 'collection_country_chart',
                    'title': _('Number of items per country (stated place of publication, including false imprints)'),
                    'url': reverse_lazy('get_collection_country_chart')
                },
                {
                    'id': 'collection_city_chart',
                    'title': _('Number of items per place of publication'),
                    'url': reverse_lazy('get_collection_city_chart')
                },
                {
                    'id': 'collection_language_chart',
                    'title': _('Number of items per language'),
                    'url': reverse_lazy('get_collection_language_chart')
                },
            ],
            [
                {
                    'id': 'collection_parisian_category_chart',
                    'title': _('Number of items per Parisian category'),
                    'url': reverse_lazy('get_collection_parisian_category_chart')
                },
                {
                    'id': 'collection_format_chart',
                    'title': _('Number of items per format'),
                    'url': reverse_lazy('get_collection_format_chart')
                },
                {
                    'id': 'collection_author_gender_chart',
                    'title': _('Number of items per author gender'),
                    'url': reverse_lazy('get_collection_author_gender_chart')
                }
            ]
        ]

        return context


def get_collections_chart(request):
    context = {}
    filter = CollectionFilter(request.GET, queryset=get_collections_for_session(request).distinct())

    max_publication_year = \
    get_collections_for_session(request).aggregate(Max('lot__collection__year_of_publication'))[
        'lot__collection__year_of_publication__max']
    if not max_publication_year:
        max_publication_year = 0
    context['max_publication_year'] = max_publication_year

    item_count_per_decade = Item.objects \
        .filter(lot__collection__in=filter.qs, edition__year_start__lte=max_publication_year) \
        .annotate(decade=10 * Substr('edition__year_start', 1, Length('edition__year_start') - 1)) \
        .values('decade') \
        .order_by('decade') \
        .annotate(count=Count('decade'))
    extra_data = {
        'item_count_per_decade': list(item_count_per_decade)
    }
    context['extra_data'] = json.dumps(extra_data)

    item_count_total = Item.objects.filter(lot__collection__in=filter.qs).count()
    context['item_count_total'] = item_count_total
    item_count_without_year = Item.objects.filter(lot__collection__in=filter.qs,
                                                  edition__year_start__isnull=True).count()
    context['item_count_without_year'] = item_count_without_year
    item_count_in_plot = Item.objects.filter(lot__collection__in=filter.qs,
                                             edition__year_start__lte=max_publication_year).count()
    context['item_count_in_plot'] = item_count_in_plot
    context['item_percentage_in_plot'] = int(
        100 * item_count_in_plot / item_count_total) if item_count_total != 0 else 0

    return render(request, 'catalogues/collection_chart.html', context=context)


def get_item_counts_for(item_field_name, collection_qs, max_publication_year):
    """
    Get item counts
    :param item_field_name: a field relative to Item (may contain relations with __)
    :param collection_qs: a Collection queryset to filter items with
    :param max_publication_year: the maximum publication year of an edition to filter items with
    :return:
    """
    edition_q = Q(edition__isnull=True) | Q(edition__year_start__isnull=True) | Q(edition__year_start__lte=max_publication_year)
    items = Item.objects.filter(lot__collection__in=collection_qs)
    items = items.filter(edition_q)
    items = items.values(item_field_name)
    targets = [item[item_field_name]
                           for item in items
                           if item[item_field_name] is not None]
    return Counter(targets).items()


def get_collection_country_chart(request):
    filter = CollectionFilter(request.GET, queryset=get_collections_for_session(request).distinct())

    max_publication_year = \
        get_collections_for_session(request).aggregate(Max('lot__collection__year_of_publication'))[
            'lot__collection__year_of_publication__max']
    if not max_publication_year:
        max_publication_year = 0

    edition_q = Q(place__edition__isnull=True) | Q(place__edition__year_start__isnull=True) \
                | Q(place__edition__year_start__lte=max_publication_year)
    item_count_per_country = [ [escape(country['name']), country['item_count'] ] for country in
        Country.objects \
            .filter(place__edition__items__lot__collection__in=filter.qs) \
            .annotate(item_count=Count('place__edition__items', edition_q))\
            .order_by('-item_count')\
            .values('name', 'item_count')
    ]
    context = {
        'chart_id': 'item_count_per_country',
        'item_count': json.dumps(item_count_per_country)
    }

    return render(request, 'generic_pie_chart.html', context=context)


def get_collection_city_chart(request):
    filter = CollectionFilter(request.GET, queryset=get_collections_for_session(request).distinct())

    max_publication_year = \
        get_collections_for_session(request).aggregate(Max('lot__collection__year_of_publication'))[
            'lot__collection__year_of_publication__max']
    if not max_publication_year:
        max_publication_year = 0

    edition_q = Q(edition__isnull=True) | Q(edition__year_start__isnull=True) | Q(
        edition__year_start__lte=max_publication_year)
    cities = Place.objects\
        .filter(edition__items__lot__collection__in=filter.qs) \
        .annotate(item_count=Count('edition__items', edition_q)) \
        .filter(item_count__gt=0) \
        .order_by('-item_count') \
        .values('name', 'item_count')

    item_with_city_count = Item.objects.filter(lot__collection__in=filter.qs, edition__place__isnull=False).count()
    item_without_city_count = Item.objects.filter(lot__collection__in=filter.qs, edition__place__isnull=True).count()

    context = {
        'chart_id': 'item_count_per_city',
        'item_count': json.dumps([
            [escape(city['name']), city['item_count'] ] for city in cities
        ]),
        'show_legend': 'false',
        'item_without_city_count': item_without_city_count,
        'percentage_item_without_city_count': round(100 * item_without_city_count
                                                    / (item_without_city_count + item_with_city_count),
                                                    2),
        'short_title_value': request.GET['short_title']
    }

    return render(request, 'catalogues/place_of_publication_pie_chart.html', context=context)


def get_collection_language_chart(request):
    filter = CollectionFilter(request.GET, queryset=get_collections_for_session(request).distinct())

    max_publication_year = \
        get_collections_for_session(request).aggregate(Max('lot__collection__year_of_publication'))[
            'lot__collection__year_of_publication__max']
    if not max_publication_year:
        max_publication_year = 0

    edition_q = Q(items__item__edition__isnull=True) | Q(items__item__edition__year_start__isnull=True) | Q(
        items__item__edition__year_start__lte=max_publication_year)
    languages = Language.objects.all()
    languages = languages.filter(items__item__lot__collection__in=filter.qs)
    languages = languages.annotate(item_count=Count('items__item', edition_q))
    languages = languages.order_by('-item_count')
    languages = languages.values('name', 'item_count')

    context = {
        'chart_id': 'item_count_per_language',
        'item_count': json.dumps([ [escape(language['name']), language['item_count']] for language in languages])
    }

    return render(request, 'generic_pie_chart.html', context=context)


def get_collection_parisian_category_chart(request):
    filter = CollectionFilter(request.GET, queryset=get_collections_for_session(request).distinct())

    max_publication_year = \
        get_collections_for_session(request).aggregate(Max('lot__collection__year_of_publication'))[
            'lot__collection__year_of_publication__max']
    if not max_publication_year:
        max_publication_year = 0
    
    counts = get_item_counts_for('parisian_category__name', filter.qs, max_publication_year)

    unclassified_items_count = Item.objects.filter(lot__collection__in=filter.qs, parisian_category__isnull=True).count()
    classified_items_count = Item.objects.filter(lot__collection__in=filter.qs, parisian_category__isnull=False).count()

    context = {
        'chart_id': 'item_count_per_parisian_category',
        'item_count': json.dumps([
            [item[0], item[1]] for item in sorted(counts, key=lambda pair: pair[1], reverse=True)
        ]),
        'unclassified_items_count': unclassified_items_count,
        'percentage_unclassified_items_count': round(100 * unclassified_items_count
                                                     / (unclassified_items_count + classified_items_count),
                                                     2)
    }

    return render(request, 'catalogues/parisian_category_pie_chart.html', context=context)


def get_collection_format_chart(request):
        filter = CollectionFilter(request.GET, queryset=get_collections_for_session(request).distinct())

        max_publication_year = \
            get_collections_for_session(request).aggregate(Max('lot__collection__year_of_publication'))[
                'lot__collection__year_of_publication__max']
        if not max_publication_year:
            max_publication_year = 0

        edition_q = Q(items__edition__isnull=True) | Q(items__edition__year_start__isnull=True) | Q(
            items__edition__year_start__lte=max_publication_year)
        formats = BookFormat.objects.filter(items__lot__collection__in=filter.qs)
        formats = formats.annotate(item_count=Count('items', edition_q))
        formats = formats.order_by('-item_count')
        formats = formats.values('name', 'item_count')

        context = {
            'chart_id': 'item_count_per_format',
            'item_count': json.dumps([[escape(format['name']), format['item_count']] for format in formats])
        }

        return render(request, 'generic_pie_chart.html', context=context)


def get_collection_author_gender_chart(request):
    filter = CollectionFilter(request.GET, queryset=get_collections_for_session(request).distinct())

    max_publication_year = \
        get_collections_for_session(request).aggregate(Max('lot__collection__year_of_publication'))[
            'lot__collection__year_of_publication__max']
    if not max_publication_year:
        max_publication_year = 0

    from functools import reduce
    from collections import defaultdict

    edition_q = Q(personitemrelation__item__edition__isnull=True) \
                | Q(personitemrelation__item__edition__year_start__isnull=True) \
                | Q(personitemrelation__item__edition__year_start__lte=max_publication_year)
    sexes = list(Person.objects.annotate(item_count=Count('personitemrelation__item',
                                      filter=Q(personitemrelation__role__name="author",
                                               personitemrelation__item__lot__collection__in=filter.qs)
                                             & edition_q,
                                      distinct=True)) \
                 .values_list('sex', 'item_count'))

    sexes_dict = defaultdict(int)
    for item in sexes:
        sexes_dict[item[0]] += item[1]
    sex_choices = dict(Person.SEX_CHOICES)
    sexes_list = sorted(sexes_dict.items(), key=lambda x: x[1], reverse=True)

    context = {
        'chart_id': 'item_count_per_author_gender',
        'item_count': json.dumps([
            [ escape(sex_choices[sex[0]]), sex[1] ] for sex in sexes_list
        ])
    }

    return render(request, 'generic_pie_chart.html', context=context)


class CollectionLocationMapView(ListView):
    model = Collection
    template_name = 'generic_location_map.html'

    def get_queryset(self):
        collections = get_collections_for_session(self.request).filter(related_places__place__latitude__isnull=False,
                                                                     related_places__place__longitude__isnull=False)
        return collections

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        context = super(CollectionLocationMapView, self).get_context_data(**kwargs)
        filter = CollectionFilter(self.request.GET, queryset=queryset)

        context['filter'] = filter
        context['object_name'] = "collection"

        context['object_list'] = filter.qs
        context['places'] = Place.objects.filter(related_collections__collection__in=filter.qs)\
                                .annotate(object_count=Count('related_collections__collection'))
        context['objects_url_name'] = 'collections'
        context['place_search_field'] = 'place'

        return context


class CollectionDetailView(PermissionRequiredMixin, DetailView):
    model = Collection

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().catalogue.first().dataset
    # End permission check

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)

        # Find the first lot for each page
        context['first_lot_on_page_dict'] = dict([
            (lot['first_lot_on_page'], lot['page_in_collection']) for lot in
            self.object.lot_set.filter(page_in_collection__isnull=False).values('page_in_collection')
                .annotate(first_lot_on_page=Min('index_in_collection')).order_by()
        ])

        # Find the first lot for each category
        # by looping over the ordered lots in the collection
        lots = self.object.lot_set.filter(category__isnull=False).values(
            'index_in_collection', 'category__bookseller_category', 'number_in_collection').order_by('index_in_collection')
        first_lot_in_category_dict = {}
        last_category = ""
        for lot in lots:
            if lot['category__bookseller_category'] != last_category or lot['number_in_collection'] == 1:
                last_category = lot['category__bookseller_category']
                first_lot_in_category_dict[lot['index_in_collection']] = lot['category__bookseller_category']
        context['first_lot_in_category_dict'] = first_lot_in_category_dict

        context['change_dataset_perm'] = self.request.user.has_perm('catalogues.change_dataset',
                                                                    self.object.catalogue.first().dataset)

        return context


class CollectionDetailBareView(CollectionDetailView):
    template_name = 'catalogues/collection_detail_bare.html'


@moderate()
class CollectionCreateView(CreateView):
    model = Collection
    template_name = 'generic_form.html'
    form_class = CollectionModelForm
    success_url = reverse_lazy('collections')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['datasets'] = get_datasets_for_session(self.request)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "collection"
        return context


@moderate()
class CollectionUpdateView(PermissionRequiredMixin, UpdateView):
    model = Collection
    template_name = 'generic_form.html'
    form_class = CollectionModelForm

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().catalogue.first().dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        collection = self.get_object()

        # Only offer things from the same dataset as this collection
        kwargs['datasets'] = [collection.catalogue.first().dataset]
        if collection.catalogue.first().dataset not in get_datasets_for_session(self.request):
            messages.warning(self.request,
                             format_html(_("The dataset this Collection belongs to, <i>{}</i>, is "
                                           "currently not selected."),
                                         collection.catalogue.first().dataset))

        return kwargs

    def get(self, request, *args, **kwargs):
        # Check whether the user has permission to view this collection
        if not self.request.user.has_perm('catalogues.change_dataset', self.get_object().catalogue.first().dataset):
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.GET.get('next') or reverse_lazy('collections')

    @put_get_variable_in_context([('next', 'next_url'),])
    @put_layout_in_context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "collection"
        return context


@moderate()
class CollectionDeleteView(PermissionRequiredMixin, DeleteView):
    model = Collection
    success_url = reverse_lazy('collections')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().catalogue.first().dataset
    # End permission check

    def get(self, request, *args, **kwargs):
        # Check whether the user has permission to view this collection
        if not self.request.user.has_perm('catalogues.change_dataset', self.get_object().catalogue.first().dataset):
            raise PermissionDenied
        return super().get(request, *args, **kwargs)


# CollectionHeldBy views
class CollectionHeldByTableView(ListView):
    model = CollectionHeldBy
    template_name = 'generic_list.html'

    def get_queryset(self):
        return CollectionHeldBy.objects.filter(collection__catalogue__dataset__in=get_datasets_for_session(self.request))

    def get_context_data(self, **kwargs):
        context = super(CollectionHeldByTableView, self).get_context_data(**kwargs)
        filter = CollectionHeldByFilter(self.request.GET, queryset=self.get_queryset())

        table = CollectionHeldByTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "collectionheldby"
        context['add_url'] = reverse_lazy('add_collectionheldby')

        return context


class CollectionHeldByDetailView(PermissionRequiredMixin, DetailView):
    model = CollectionHeldBy
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection.catalogue.first().dataset
    # End permission check


class CollectionHeldByCreateView(CreateView):
    model = CollectionHeldBy
    template_name = 'generic_form.html'
    form_class = CollectionHeldByModelForm
    success_url = reverse_lazy('collectionheldbys')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "collectionheldby"
        return context


class CollectionHeldByUpdateView(UpdateView):
    model = CollectionHeldBy
    template_name = 'generic_form.html'
    form_class = CollectionHeldByModelForm
    success_url = reverse_lazy('collectionheldbys')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "collectionheldby"
        return context


class CollectionHeldByDeleteView(DeleteView):
    model = CollectionHeldBy
    success_url = reverse_lazy('collectionheldbys')


# CollectionType views
class CollectionTypeTableView(ListView):
    model = CollectionType
    template_name = 'generic_list.html'

    def get_queryset(self):
        return CollectionType.objects.all()

    def get_context_data(self, **kwargs):
        context = super(CollectionTypeTableView, self).get_context_data(**kwargs)
        filter = CollectionTypeFilter(self.request.GET, queryset=self.get_queryset())

        table = CollectionTypeTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "collectiontype"
        context['add_url'] = reverse_lazy('add_collectiontype')

        return context


class CollectionTypeDetailView(DetailView):
    model = CollectionType


class CollectionTypeCreateView(CreateView):
    model = CollectionType
    template_name = 'generic_form.html'
    form_class = CollectionTypeModelForm
    success_url = reverse_lazy('collectiontypes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "collectiontype"
        return context


class CollectionTypeUpdateView(UpdateView):
    model = CollectionType
    template_name = 'generic_form.html'
    form_class = CollectionTypeModelForm
    success_url = reverse_lazy('collectiontypes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "collectiontype"
        return context


class CollectionTypeDeleteView(DeleteView):
    model = CollectionType
    success_url = reverse_lazy('collectiontypes')


# CollectionCollectionTypeRelation views
class CollectionCollectionTypeRelationTableView(ListView):
    model = CollectionCollectionTypeRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return CollectionCollectionTypeRelation.objects\
            .filter(collection__catalogue__dataset__in=get_datasets_for_session(self.request))

    def get_context_data(self, **kwargs):
        context = super(CollectionCollectionTypeRelationTableView, self).get_context_data(**kwargs)
        filter = CollectionCollectionTypeRelationFilter(self.request.GET, queryset=self.get_queryset())

        table = CollectionCollectionTypeRelationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "collectioncollectiontyperelation"
        context['add_url'] = reverse_lazy('add_collectioncollectiontyperelation')

        return context


class CollectionCollectionTypeRelationDetailView(PermissionRequiredMixin, DetailView):
    model = CollectionCollectionTypeRelation
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection.catalogue.first().dataset
    # End permission check


class CollectionCollectionTypeRelationCreateView(CreateView):
    model = CollectionCollectionTypeRelation
    template_name = 'generic_form.html'
    form_class = CollectionCollectionTypeRelationModelForm
    success_url = reverse_lazy('collectioncollectiontyperelations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['collections'] = get_collections_for_session(self.request)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "collectioncollectiontyperelation"
        return context


class CollectionCollectionTypeRelationUpdateView(PermissionRequiredMixin, UpdateView):
    model = CollectionCollectionTypeRelation
    template_name = 'generic_form.html'
    form_class = CollectionCollectionTypeRelationModelForm
    success_url = reverse_lazy('collectioncollectiontyperelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().collection.catalogue.first().dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        relation = self.get_object()
        kwargs['collections'] = get_collections_for_session(
            self.request,
            relation.collection
        )
        if relation.collection.catalogue.first().dataset not in get_datasets_for_session(self.request):
            messages.warning(self.request,
                             format_html(_("The dataset this CollectionCollectionTypeRelation belongs to, <i>{}</i>, is "
                                           "currently not selected."),
                                         relation.collection.catalogue.first().dataset))

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "collectioncollectiontyperelation"
        return context


class CollectionCollectionTypeRelationDeleteView(PermissionRequiredMixin, DeleteView):
    model = CollectionCollectionTypeRelation
    success_url = reverse_lazy('collectioncollectiontyperelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().collection.catalogue.first().dataset
    # End permission check


# Catalogue views
class CatalogueTableView(ListView):
    model = Catalogue
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Catalogue.objects.filter(dataset__in=get_datasets_for_session(self.request)).order_by('name')

    def get_context_data(self, **kwargs):
        datasets_permitted = get_permitted_datasets_for_session(self.request)

        context = super(CatalogueTableView, self).get_context_data(**kwargs)
        filter = CatalogueFilter(self.request.GET, queryset=self.get_queryset())

        table = CatalogueTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "catalogue"
        context['add_url'] = reverse_lazy('add_catalogue') if datasets_permitted else None

        return context


class CatalogueDetailView(PermissionRequiredMixin, GenericDetailView):
    model = Catalogue
    object_fields = ['name', 'dataset']
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().dataset
    # End permission check


class CatalogueCreateView(CreateView):
    model = Catalogue
    template_name = 'generic_form.html'
    form_class = CatalogueModelForm
    success_url = reverse_lazy('catalogues')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['datasets'] = get_objects_for_user(self.request.user, 'catalogues.change_dataset') \
                             or get_dataset_for_anonymoususer()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "catalogue"
        return context


class CatalogueUpdateView(PermissionRequiredMixin, UpdateView):
    model = Catalogue
    template_name = 'generic_form.html'
    form_class = CatalogueModelForm
    success_url = reverse_lazy('catalogues')

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
        context['object_name'] = "catalogue"
        return context


class CatalogueDeleteView(PermissionRequiredMixin, DeleteView):
    model = Catalogue
    success_url = reverse_lazy('catalogues')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().dataset
    # End permission check


# CatalogueYear views
class CatalogueYearTableView(ListView):
    model = CatalogueYear
    template_name = 'generic_list.html'

    def get_queryset(self):
        return CatalogueYear.objects.all()

    def get_context_data(self, **kwargs):
        context = super(CatalogueYearTableView, self).get_context_data(**kwargs)
        filter = CatalogueYearFilter(self.request.GET, queryset=self.get_queryset())

        table = CatalogueYearTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "catalogueyear"
        context['add_url'] = reverse_lazy('add_catalogueyear')

        return context


class CatalogueYearDetailView(DetailView):
    model = CatalogueYear


class CatalogueYearCreateView(CreateView):
    model = CatalogueYear
    template_name = 'generic_form.html'
    form_class = CatalogueYearModelForm
    success_url = reverse_lazy('catalogueyears')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "catalogueyear"
        return context


class CatalogueYearUpdateView(UpdateView):
    model = CatalogueYear
    template_name = 'generic_form.html'
    form_class = CatalogueYearModelForm
    success_url = reverse_lazy('catalogueyears')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "catalogueyear"
        return context


class CatalogueYearDeleteView(DeleteView):
    model = CatalogueYear
    success_url = reverse_lazy('catalogueyears')


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
        return Lot.objects.filter(collection__catalogue__dataset__in=get_datasets_for_session(self.request))\
            .order_by('collection__year_of_publication', 'collection__short_title', 'index_in_collection',
                                    'lot_as_listed_in_collection')

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
    object_fields = ['collection', 'number_in_collection', 'page_in_collection', 'sales_price',
                     'lot_as_listed_in_collection', 'index_in_collection', 'category']

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection.catalogue.first().dataset
    # End permission check


@moderate()
class LotCreateView(CreateView):
    model = Lot
    template_name = 'generic_form.html'
    form_class = LotModelForm
    success_url = reverse_lazy('lots')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['collections'] = get_collections_for_session(self.request)
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
        return self.get_object().collection.catalogue.first().dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        lot = self.get_object()
        kwargs['collections'] = get_collections_for_session(
            self.request,
            lot.collection
        )
        if lot.collection.catalogue.first().dataset not in get_datasets_for_session(self.request):
            messages.warning(self.request,
                             format_html(_("The dataset this Lot belongs to, <i>{}</i>, is "
                                           "currently not selected."),
                                         lot.collection.catalogue.first().dataset))
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
        return self.get_object().collection.catalogue.first().dataset
    # End permission check


def previous_lot_view(request, pk, index):
    try:
        lot = Lot.objects.get(collection__uuid=pk, index_in_collection=index)
        if not request.user.has_perm('catalogues.view_dataset', lot.collection.catalogue.first().dataset):
            raise PermissionDenied()
        return JsonResponse({
            'success': True,
            'lot_as_listed_in_collection': lot.lot_as_listed_in_collection,
            'index_in_collection': lot.index_in_collection
        })
    except ObjectDoesNotExist:
        return JsonResponse({
            'success': False
        })


def expand_lot_view(request, pk):
    lot = get_object_or_404(Lot, pk=pk)
    if not request.user.has_perm('catalogues.view_dataset', lot.collection.catalogue.first().dataset):
        raise PermissionDenied()
    next_url = reverse_lazy('collection_detail_bare', args=[str(lot.collection.uuid)])

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
                                           catalogue=lot.collection.catalogue.first(), edition=edition)
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
    Add a lot at a certain position in the list of lots of a collection.
    The position is determined as *before* the lot with 'pk' as the id.
    If the 'page' url parameter is set, it means the page before the page of the selected lot.
    If the 'category' url parameter is set, it means the category before the category of the selected lot.
    :param request: 
    :param pk: 
    :return: 
    """
    lot_after = get_object_or_404(Lot, pk=pk)
    if not request.user.has_perm('catalogues.change_dataset', lot_after.collection.catalogue.first().dataset):
        raise PermissionDenied()

    # Determine whether there is a lot before the selected position
    try:
        lot_before = Lot.objects.filter(collection=lot_after.collection, index_in_collection__lt=lot_after.index_in_collection)\
            .order_by('-index_in_collection').first()
    except:
        lot_before = None

    next_url = reverse_lazy('collection_detail_bare', args=[str(lot_after.collection.uuid)])
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
                page = lot_before.page_in_collection
            elif lot_after.page_in_collection > 1:
                page = lot_after.page_in_collection - 1
            else:
                page = lot_after.page_in_collection
        else:
            page = lot_after.page_in_collection

        index = lot_after.index_in_collection

        form = AddLotBeforeForm(category=category, page=page, index=index, collection=lot_after.collection)
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
    Add a lot at the end of a collection
    :param request:
    :param pk:
    :return:
    """
    collection = get_object_or_404(Collection, pk=pk)
    if not request.user.has_perm('catalogues.change_dataset', collection.catalogue.first().dataset):
        raise PermissionDenied()
    last_lot = Lot.objects.filter(collection=collection).order_by('-index_in_collection').first()

    next_url = reverse_lazy('collection_detail_bare', args=[str(collection.uuid)])
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
        form = AddLotAtEndForm(category=category, page=page, index=index, collection=collection)
    else:
        form = AddLotAtEndForm()

    context = {
        'form': form,
        'extended_layout': 'barelayout.html',
        'action': _("Add lot"),
        'next_url': next_url
    }

    return render(request, 'generic_form.html', context=context)


# PersonCollectionRelation views
class PersonCollectionRelationTableView(ListView):
    model = PersonCollectionRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return PersonCollectionRelation.objects.filter(
            collection__catalogue__dataset__in=get_datasets_for_session(self.request)
        )

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


class PersonCollectionRelationDetailView(PermissionRequiredMixin, DetailView):
    model = PersonCollectionRelation
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection.catalogue.first().dataset
    # End permission check


class PersonCollectionRelationCreateView(CreateView):
    model = PersonCollectionRelation
    template_name = 'generic_form.html'
    form_class = PersonCollectionRelationModelForm
    success_url = reverse_lazy('personcollectionrelations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['collections'] = get_collections_for_session(self.request)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "personcollectionrelation"
        return context


class PersonCollectionRelationUpdateView(PermissionRequiredMixin, UpdateView):
    model = PersonCollectionRelation
    template_name = 'generic_form.html'
    form_class = PersonCollectionRelationModelForm
    success_url = reverse_lazy('personcollectionrelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection.catalogue.first().dataset

    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        personcollectionrelation = self.get_object()
        kwargs['collections'] = get_collections_for_session(
            self.request,
            personcollectionrelation.collection
        )
        if personcollectionrelation.collection.catalogue.first().dataset not in get_datasets_for_session(self.request):
            messages.warning(self.request,
                             format_html(_("The dataset this PersonCollectionRelation belongs to, <i>{}</i>, is "
                                           "currently not selected."),
                                         personcollectionrelation.collection.catalogue.first().dataset))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "personcollectionrelation"
        return context


class PersonCollectionRelationDeleteView(PermissionRequiredMixin, DeleteView):
    model = PersonCollectionRelation
    success_url = reverse_lazy('personcollectionrelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection.catalogue.first().dataset
    # End permission check


# PersonCollectionRelationRole views
class PersonCollectionRelationRoleTableView(ListView):
    model = PersonCollectionRelationRole
    template_name = 'generic_list.html'

    def get_queryset(self):
        return PersonCollectionRelationRole.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PersonCollectionRelationRoleTableView, self).get_context_data(**kwargs)
        filter = PersonCollectionRelationRoleFilter(self.request.GET, queryset=self.get_queryset())

        table = PersonCollectionRelationRoleTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "personcollectionrelationrole"
        context['add_url'] = reverse_lazy('add_personcollectionrelationrole')

        return context


class PersonCollectionRelationRoleDetailView(DetailView):
    model = PersonCollectionRelationRole


class PersonCollectionRelationRoleCreateView(CreateView):
    model = PersonCollectionRelationRole
    template_name = 'generic_form.html'
    form_class = PersonCollectionRelationRoleModelForm
    success_url = reverse_lazy('personcollectionrelationroles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "personcollectionrelationrole"
        return context


class PersonCollectionRelationRoleUpdateView(UpdateView):
    model = PersonCollectionRelationRole
    template_name = 'generic_form.html'
    form_class = PersonCollectionRelationRoleModelForm
    success_url = reverse_lazy('personcollectionrelationroles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "personcollectionrelationrole"
        return context


class PersonCollectionRelationRoleDeleteView(DeleteView):
    model = PersonCollectionRelationRole
    success_url = reverse_lazy('personcollectionrelationroles')


# PersonCatalogueRelation views
class PersonCatalogueRelationTableView(ListView):
    model = PersonCatalogueRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return PersonCatalogueRelation.objects.filter(catalogue__dataset__in=get_datasets_for_session(self.request))

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
    model = PersonCatalogueRelation
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().catalogue.first().dataset
    # End permission check


class PersonCatalogueRelationCreateView(CreateView):
    model = PersonCatalogueRelation
    template_name = 'generic_form.html'
    form_class = PersonCatalogueRelationModelForm
    success_url = reverse_lazy('personcataloguerelations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['catalogues'] = Catalogue.objects.filter(dataset__in=get_datasets_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "personcataloguerelation"
        return context


class PersonCatalogueRelationUpdateView(PermissionRequiredMixin, UpdateView):
    model = PersonCatalogueRelation
    template_name = 'generic_form.html'
    form_class = PersonCatalogueRelationModelForm
    success_url = reverse_lazy('personcataloguerelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().catalogue.dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        personcataloguerelation = self.get_object()
        kwargs['catalogues'] = Catalogue.objects.filter(
            Q(dataset__in=get_datasets_for_session(self.request))
            | Q(uuid=personcataloguerelation.catalogue.uuid)
        )
        if personcataloguerelation.catalogue.dataset not in get_datasets_for_session(self.request):
            messages.warning(self.request,
                             format_html(_("The dataset this PersonCatalogueRelation belongs to, <i>{}</i>, is "
                                           "currently not selected."),
                                         personcataloguerelation.catalogue.dataset))

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "personcataloguerelation"
        return context


class PersonCatalogueRelationDeleteView(PermissionRequiredMixin, DeleteView):
    model = PersonCatalogueRelation
    success_url = reverse_lazy('personcataloguerelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().catalogue.first().dataset
    # End permission check


class CollectionPlaceRelationTableView(ListView):
    model = CollectionPlaceRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return CollectionPlaceRelation.objects\
            .filter(collection__catalogue__dataset__in=get_datasets_for_session(self.request))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter = CollectionPlaceRelationFilter(self.request.GET, queryset=self.get_queryset())

        table = CollectionPlaceRelationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name_plural'] = self.model._meta.verbose_name_plural
        context['add_url'] = reverse_lazy('add_collectionplacerelation')

        return context


class CollectionPlaceRelationDetailView(PermissionRequiredMixin, DetailView):
    model = CollectionPlaceRelation
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection.catalogue.first().dataset
    # End permission check


class CollectionPlaceRelationCreateView(CreateView):
    model = CollectionPlaceRelation
    template_name = 'generic_form.html'
    form_class = CollectionPlaceRelationModelForm
    success_url = reverse_lazy('collectionplacerelations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['collections'] = get_collections_for_session(self.request)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "collection publication place"
        return context


class CollectionPlaceRelationUpdateView(PermissionRequiredMixin, UpdateView):
    model = CollectionPlaceRelation
    template_name = 'generic_form.html'
    form_class = CollectionPlaceRelationModelForm
    success_url = reverse_lazy('collectionplacerelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().collection.catalogue.first().dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        relation = self.get_object()
        kwargs['collections'] = get_collections_for_session(
            self.request,
            relation.collection
        )
        if relation.collection.catalogue.first().dataset not in get_datasets_for_session(self.request):
            messages.warning(self.request,
                             format_html(_("The dataset this CollectionPlaceRelation belongs to, <i>{}</i>, is "
                                           "currently not selected."),
                                         relation.collection.catalogue.first().dataset))

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "collection publication place"
        return context


class CollectionPlaceRelationDeleteView(PermissionRequiredMixin, DeleteView):
    model = CollectionPlaceRelation
    success_url = reverse_lazy('collectionplacerelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().collection.catalogue.first().dataset
    # End permission check


# Category views
class CategoryTableView(ListView):
    model = Category
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Category.objects.filter(collection__catalogue__dataset__in=get_datasets_for_session(self.request))

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
    object_fields = ['collection', 'parent', 'bookseller_category', 'parisian_category']
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().collection.catalogue.first().dataset
    # End permission check


class CategoryCreateView(CreateView):
    model = Category
    template_name = 'generic_form.html'
    form_class = CategoryModelForm
    success_url = reverse_lazy('categories')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['collections'] = get_collections_for_session(self.request)
        kwargs['categories'] = Category.objects.filter(collection__catalogue__dataset__in=get_datasets_for_session(self.request))
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
        return self.get_object().collection.catalogue.first().dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        category = self.get_object()
        kwargs['collections'] = get_collections_for_session(
            self.request,
            category.collection
        )
        kwargs['categories'] = Category.objects.filter(
            Q(collection__catalogue__dataset__in=get_datasets_for_session(self.request))
            | Q(pk=category.pk)
        )
        if category.collection.catalogue.first().dataset not in get_datasets_for_session(self.request):
            messages.warning(self.request,
                             format_html(_("The dataset this Category belongs to, <i>{}</i>, is "
                                           "currently not selected."),
                                         category.collection.catalogue.first().dataset))
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
        return self.get_object().collection.catalogue.first().dataset
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


# CollectionPlaceRelationType views
class CollectionPlaceRelationTypeTableView(ListView):
    model = CollectionPlaceRelationType
    template_name = 'generic_list.html'

    def get_queryset(self):
        return CollectionPlaceRelationType.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter = CollectionPlaceRelationTypeFilter(self.request.GET, queryset=self.get_queryset())

        table = CollectionPlaceRelationTypeTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name_plural'] = self.model._meta.verbose_name_plural
        context['add_url'] = reverse_lazy('add_collectionplacerelationtype')

        return context


class CollectionPlaceRelationTypeDetailView(DetailView):
    model = CollectionPlaceRelationType


class CollectionPlaceRelationTypeCreateView(CreateView):
    model = CollectionPlaceRelationType
    template_name = 'generic_form.html'
    form_class = CollectionPlaceRelationTypeModelForm
    success_url = reverse_lazy('collectionplacerelationtypes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "collectionplacerelationtype"
        return context


class CollectionPlaceRelationTypeUpdateView(UpdateView):
    model = CollectionPlaceRelationType
    template_name = 'generic_form.html'
    form_class = CollectionPlaceRelationTypeModelForm
    success_url = reverse_lazy('collectionplacerelationtypes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "collectionplacerelationtype"
        return context


class CollectionPlaceRelationTypeDeleteView(DeleteView):
    model = CollectionPlaceRelationType
    success_url = reverse_lazy('collectionplacerelationtypes')
