from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.forms import formset_factory
from django_tables2.config import RequestConfig
from django_tables2.export.export import TableExport

from django.utils.translation import gettext_lazy as _
from django.utils.html import escape
from django.shortcuts import get_object_or_404, render
from django.db import transaction
from django.db.models import Case, When

import django_tables2
from guardian.shortcuts import get_objects_for_user, get_perms
from guardian.mixins import PermissionRequiredMixin
from django_select2.views import AutoResponseView

from dal import autocomplete
from django.http import JsonResponse
import re
import json

from catalogues.tools import get_datasets_for_session
from ..forms import *
from ..filters import *
from ..tables import *

from apiconnectors.viafapi import ViafAPI

from catalogues.models import Dataset
from persons.forms import PersonModelForm
from mediate.views import GenericDetailView
from catalogues.views.views import get_collections_for_session
from catalogues.tools import get_datasets_for_session, get_permitted_datasets_for_session
from simplemoderation.models import Moderation, ModerationAction

from simplemoderation.tools import moderate


# BookFormat views
class BookFormatTableView(ListView):
    model = BookFormat
    template_name = 'generic_list.html'

    def get_queryset(self):
        return BookFormat.objects.all()

    def get_context_data(self, **kwargs):
        context = super(BookFormatTableView, self).get_context_data(**kwargs)
        filter = BookFormatFilter(self.request.GET, queryset=self.get_queryset())

        table = BookFormatTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "bookformat"
        context['add_url'] = reverse_lazy('add_bookformat')

        return context


class BookFormatDetailView(DetailView):
    model = BookFormat


class BookFormatCreateView(CreateView):
    model = BookFormat
    template_name = 'generic_form.html'
    form_class = BookFormatModelForm
    success_url = reverse_lazy('bookformats')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "bookformat"
        return context


class BookFormatUpdateView(UpdateView):
    model = BookFormat
    template_name = 'generic_form.html'
    form_class = BookFormatModelForm
    success_url = reverse_lazy('bookformats')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "bookformat"
        return context


class BookFormatDeleteView(DeleteView):
    model = BookFormat
    success_url = reverse_lazy('bookformats')


# Item views
PersonItemRelationAddFormSet = formset_factory(PersonItemRelationAddForm, extra=1)


class ItemTableView(ListView):
    model = Item
    template_name = 'generic_list.html'

    def get_queryset(self):
        #NEW
        items = Item.objects \
            .filter(dataset_uuid__in=[dataset.uuid for dataset in get_datasets_for_session(self.request)]) \
            .order_by('collection_year_of_publication', 'collection_short_title',
                                      'lot_index_in_collection', 'index_in_lot', 'lot_lot_as_listed_in_collection')

        lot_uuid = self.request.GET.get('lot__uuid')
        if lot_uuid:
            items = items.filter(lot__uuid=uuid.UUID(lot_uuid))
        return items

    def get(self, request, *args, **kwargs):
        # Handle the _export query
        export_format = request.GET.get('_export', None)
        if TableExport.is_valid_format(export_format):
            filter = ItemFilter(self.request.GET, queryset=self.get_queryset())
            table = ItemTable(filter.qs)
            RequestConfig(request).configure(table)
            exporter = TableExport(export_format, table,
                                   exclude_columns=('uuid', 'manage_works', 'manage_persons', 'checkbox'))
            return exporter.response('table.{}'.format(export_format))
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        datasets_permitted = get_permitted_datasets_for_session(self.request)

        context = super(ItemTableView, self).get_context_data(**kwargs)
        filter = ItemFilter(self.request.GET, queryset=self.get_queryset())

        table = ItemTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)
        if not datasets_permitted:
            table.exclude = ('checkbox', 'manage_works', 'manage_persons')

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "item"

        context['add_url'] = reverse_lazy('add_item') if datasets_permitted else None

        context['map_url'] = reverse_lazy('itemsmap')

        context['addanother_person_form'] = PersonModelForm()
        context['batch_edit_options'] = [
            {
                'id': 'add_person',
                'label': _("Add person"),
                'url': reverse_lazy('add_persontoitems'),
                'form_set': PersonItemRelationAddFormSet
            },
            {
                'id': 'set_editionplaces',
                'label': _("Set real publication places"),
                'url': reverse_lazy('set_editionplaces_for_items'),
                'form': EditionPlacesForm
            },
            {
                'id': 'set_publisher',
                'label': _("Set publisher"),
                'url': reverse_lazy('set_publisher_for_items'),
                'form': PublisherForm
            },
            {
                'id': 'set_bookformat',
                'label': _("Set book format"),
                'url': reverse_lazy('set_bookformat'),
                'form': ItemFormatForm
            },
            {
                'id': 'add_language',
                'label': _("Add language"),
                'url': reverse_lazy('add_language_to_items'),
                'form': ItemLanguageForm
            },
            {
                'id': 'add_type',
                'label': _("Add type"),
                'url': reverse_lazy('add_type_to_items'),
                'form': ItemItemTypeForm
            },
            {
                'id': 'add_tags',
                'label': _("Add tags"),
                'url': reverse_lazy('add_tags_to_items'),
                'form': ItemTagsForm
            },
            {
                'id': 'add_works',
                'label': _("Add works"),
                'url': reverse_lazy('add_works_to_items'),
                'form': ItemWorksForm
            },
            {
                'id': 'add_materialdetails',
                'label': _("Add material details"),
                'url': reverse_lazy('add_materialdetails_to_items'),
                'form': ItemMaterialDetailsForm
            },
            {
                'id': 'add_parisiancategories',
                'label': _("Add Parisian categories"),
                'url': reverse_lazy('add_parisiancategories_to_items'),
                'form': ItemParisianCategoriesForm
            },
            {
                'id': 'toggle_uncountable_book_items',
                'label': _("Toggle uncountable book items"),
                'url': reverse_lazy('toggle_uncountable_book_items'),
                'message': _("The uncountable book items field of the selected items will be toggled."),
                'form': None,
            }
        ] if datasets_permitted else None

        context['per_page_choices'] = [25, 50, 100, 500, 1000]

        return context


class PersonAndRoleAutocompleteView(AutoResponseView):
    page_size = 10

    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '')
        page = int(request.GET.get('page', 1))
        begin = (page - 1) * self.page_size
        end = page * self.page_size
        person_query = Q(person__short_name__icontains=term)
        role_query = Q(role__name__icontains=term)

        person_item_relations = PersonItemRelation.objects\
                .filter(item__lot__collection__catalogue__dataset__in=get_datasets_for_session(request)) \
                .filter(person_query | role_query)\
                .values('person', 'person__short_name', 'role', 'role__name')\
                .distinct().order_by('person__short_name')[begin:end]

        more = True
        if len(person_item_relations) != self.page_size:
            more = False

        person_roles = [
            {
                'id': "{}|{}".format(rel['person'], rel['role']),
                'text': "{} - {}".format(rel['person__short_name'], rel['role__name'])
            }
            for rel in person_item_relations
        ]
        return JsonResponse({
            'results': person_roles,
            'more': more
        })


class TaggedItemTableView(ListView):
    model = Item
    template_name = 'generic_list.html'

    def get_queryset(self):
        tags = get_objects_for_user(self.request.user, 'tagme.view_entities_with_this_tag')
        return Item.objects\
            .filter(lot__collection_id__in=get_collections_for_session(self.request))\
            .filter(tags__tag__in=tags)

    def get(self, request, *args, **kwargs):
        # Handle the _export query
        export_format = request.GET.get('_export', None)
        if TableExport.is_valid_format(export_format):
            filter = ItemFilter(self.request.GET, queryset=self.get_queryset())
            table = TaggedItemTable(filter.qs)
            RequestConfig(request).configure(table)
            exporter = TableExport(export_format, table,
                                   exclude_columns=('uuid', 'manage_works', 'manage_persons', 'checkbox'))
            return exporter.response('table.{}'.format(export_format))
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter = ItemFilter(self.request.GET, queryset=self.get_queryset())

        table = TaggedItemTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "item"
        context['export'] = {
            'csv': 'CSV',
            'xlsx': 'Excel'
        }

        return context


class ItemTagRankingTableView(ListView):
    model = Tag
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Tag.objects.filter(namespace__iexact='item')

    def get_context_data(self, **kwargs):
        context = super(ItemTagRankingTableView, self).get_context_data(**kwargs)
        filter = ItemTagRankingFilter(self.request.GET, queryset=self.get_queryset(), request=self.request)

        table = ItemTagRankingTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table
        context['object_name'] = "tag"

        return context



class ItemLocationMapView(ListView):
    model = Item
    template_name = 'generic_location_map.html'

    def get_queryset(self):
        items = Item.objects\
            .filter(lot__collection_id__in=get_collections_for_session(self.request))\
            .filter(edition__place__latitude__isnull=False, edition__place__longitude__isnull=False)
        return items

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        context = super(ItemLocationMapView, self).get_context_data(**kwargs)
        filter = ItemFilter(self.request.GET, queryset=queryset)

        context['filter'] = filter
        context['object_name'] = "item"

        context['object_list'] = filter.qs
        context['places'] = Place.objects.filter(edition__items__in=filter.qs)\
                                .annotate(object_count=Count('edition__items'))
        context['objects_url_name'] = 'items'
        context['place_search_field'] = 'edition_place'
        context['page_heading'] = _("Item: places of publication")

        return context


class ItemDetailView(PermissionRequiredMixin, DetailView):
    model = Item
    template_name = 'items/item_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().lot.collection.catalogue.first().dataset
    # End permission check


class ItemCreateView(CreateView):
    model = Item
    template_name = 'generic_form.html'
    form_class = ItemModelForm
    success_url = reverse_lazy('items')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['catalogues'] = Catalogue.objects.filter(dataset__in=get_datasets_for_session(self.request))
        kwargs['lots'] = Lot.objects.filter(collection__in=get_collections_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "item"
        return context


@moderate(action=ModerationAction.UPDATE)
class ItemUpdateView(PermissionRequiredMixin, UpdateView):
    model = Item
    template_name = 'generic_form.html'
    form_class = ItemModelForm
    success_url = reverse_lazy('items')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().lot.collection.catalogue.first().dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['catalogues'] = Catalogue.objects.filter(dataset__in=get_datasets_for_session(self.request))
        kwargs['lots'] = Lot.objects.filter(collection__in=get_collections_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "item"
        return context


class ItemDeleteView(PermissionRequiredMixin, DeleteView):
    model = Item
    success_url = reverse_lazy('items')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().lot.collection.catalogue.first().dataset
    # End permission check

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', self.success_url)


# ItemAuthor views
class ItemAuthorTableView(ListView):
    model = ItemAuthor
    template_name = 'generic_list.html'

    def get_queryset(self):
        return ItemAuthor.objects.filter(item__lot__collection__in=get_collections_for_session(self.request))

    def get_context_data(self, **kwargs):
        context = super(ItemAuthorTableView, self).get_context_data(**kwargs)
        filter = ItemAuthorFilter(self.request.GET, queryset=self.get_queryset())

        table = ItemAuthorTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "itemauthor"
        context['add_url'] = reverse_lazy('add_itemauthor')

        return context


class ItemAuthorDetailView(PermissionRequiredMixin, DetailView):
    model = ItemAuthor
    template_name = 'items/item_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check


class ItemAuthorCreateView(CreateView):
    model = ItemAuthor
    template_name = 'generic_form.html'
    form_class = ItemAuthorModelForm
    success_url = reverse_lazy('itemauthors')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['items'] = Item.objects.filter(lot__collection__in=get_collections_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "itemauthor"
        return context


class ItemAuthorUpdateView(PermissionRequiredMixin, UpdateView):
    model = ItemAuthor
    template_name = 'generic_form.html'
    form_class = ItemAuthorModelForm
    success_url = reverse_lazy('itemauthors')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['items'] = Item.objects.filter(lot__collection__in=get_collections_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "itemauthor"
        return context


class ItemAuthorDeleteView(PermissionRequiredMixin, DeleteView):
    model = ItemAuthor
    success_url = reverse_lazy('itemauthors')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check


# ItemItemTypeRelation views
class ItemItemTypeRelationTableView(ListView):
    model = ItemItemTypeRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return ItemItemTypeRelation.objects.filter(item__lot__collection__in=get_collections_for_session(self.request))

    def get_context_data(self, **kwargs):
        context = super(ItemItemTypeRelationTableView, self).get_context_data(**kwargs)
        filter = ItemItemTypeRelationFilter(self.request.GET, queryset=self.get_queryset())

        table = ItemItemTypeRelationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "itemitemtyperelation"
        context['add_url'] = reverse_lazy('add_itemitemtyperelation')

        return context


class ItemItemTypeRelationDetailView(PermissionRequiredMixin, DetailView):
    model = ItemItemTypeRelation
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check


class ItemItemTypeRelationCreateView(CreateView):
    model = ItemItemTypeRelation
    template_name = 'generic_form.html'
    form_class = ItemItemTypeRelationModelForm
    success_url = reverse_lazy('itemitemtyperelations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['items'] = Item.objects.filter(lot__collection__in=get_collections_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "itemitemtyperelation"
        return context


class ItemItemTypeRelationUpdateView(PermissionRequiredMixin, UpdateView):
    model = ItemItemTypeRelation
    template_name = 'generic_form.html'
    form_class = ItemItemTypeRelationModelForm
    success_url = reverse_lazy('itemitemtyperelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['items'] = Item.objects.filter(lot__collection__in=get_collections_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "itemitemtyperelation"
        return context


class ItemItemTypeRelationDeleteView(PermissionRequiredMixin, DeleteView):
    model = ItemItemTypeRelation
    success_url = reverse_lazy('itemitemtyperelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check


# ItemLanguageRelation views
class ItemLanguageRelationTableView(ListView):
    model = ItemLanguageRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return ItemLanguageRelation.objects.filter(item__lot__collection__in=get_collections_for_session(self.request))

    def get_context_data(self, **kwargs):
        context = super(ItemLanguageRelationTableView, self).get_context_data(**kwargs)
        filter = ItemLanguageRelationFilter(self.request.GET, queryset=self.get_queryset())

        table = ItemLanguageRelationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "itemlanguagerelation"
        context['add_url'] = reverse_lazy('add_itemlanguagerelation')

        return context


class ItemLanguageRelationDetailView(PermissionRequiredMixin, DetailView):
    model = ItemLanguageRelation
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check


class ItemLanguageRelationCreateView(CreateView):
    model = ItemLanguageRelation
    template_name = 'generic_form.html'
    form_class = ItemLanguageRelationModelForm
    success_url = reverse_lazy('itemlanguagerelations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['items'] = Item.objects.filter(lot__collection__in=get_collections_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "itemlanguagerelation"
        return context


class ItemLanguageRelationUpdateView(PermissionRequiredMixin, UpdateView):
    model = ItemLanguageRelation
    template_name = 'generic_form.html'
    form_class = ItemLanguageRelationModelForm
    success_url = reverse_lazy('itemlanguagerelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['items'] = Item.objects.filter(lot__collection__in=get_collections_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "itemlanguagerelation"
        return context


class ItemLanguageRelationDeleteView(PermissionRequiredMixin, DeleteView):
    model = ItemLanguageRelation
    success_url = reverse_lazy('itemlanguagerelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check


# ItemMaterialDetailsRelation views
class ItemMaterialDetailsRelationTableView(ListView):
    model = ItemMaterialDetailsRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return ItemMaterialDetailsRelation.objects.filter(
            item__lot__collection__in=get_collections_for_session(self.request)
        )

    def get_context_data(self, **kwargs):
        context = super(ItemMaterialDetailsRelationTableView, self).get_context_data(**kwargs)
        filter = ItemMaterialDetailsRelationFilter(self.request.GET, queryset=self.get_queryset())

        table = ItemMaterialDetailsRelationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "itemmaterialdetailsrelation"
        context['add_url'] = reverse_lazy('add_itemmaterialdetailsrelation')

        return context


class ItemMaterialDetailsRelationDetailView(PermissionRequiredMixin, DetailView):
    model = ItemMaterialDetailsRelation
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check


class ItemMaterialDetailsRelationCreateView(CreateView):
    model = ItemMaterialDetailsRelation
    template_name = 'generic_form.html'
    form_class = ItemMaterialDetailsRelationModelForm
    success_url = reverse_lazy('itemmaterialdetailsrelations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['items'] = Item.objects.filter(lot__collection__in=get_collections_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "itemmaterialdetailsrelation"
        return context


class ItemMaterialDetailsRelationUpdateView(PermissionRequiredMixin, UpdateView):
    model = ItemMaterialDetailsRelation
    template_name = 'generic_form.html'
    form_class = ItemMaterialDetailsRelationModelForm
    success_url = reverse_lazy('itemmaterialdetailsrelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['items'] = Item.objects.filter(lot__collection__in=get_collections_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "itemmaterialdetailsrelation"
        return context


class ItemMaterialDetailsRelationDeleteView(PermissionRequiredMixin, DeleteView):
    model = ItemMaterialDetailsRelation
    success_url = reverse_lazy('itemmaterialdetailsrelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check


# ItemType views
class ItemTypeTableView(ListView):
    model = ItemType
    template_name = 'generic_list.html'

    def get_queryset(self):
        return ItemType.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ItemTypeTableView, self).get_context_data(**kwargs)
        filter = ItemTypeFilter(self.request.GET, queryset=self.get_queryset())

        table = ItemTypeTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "itemtype"
        context['add_url'] = reverse_lazy('add_itemtype')

        return context


class ItemTypeDetailView(DetailView):
    model = ItemType


class ItemTypeCreateView(CreateView):
    model = ItemType
    template_name = 'generic_form.html'
    form_class = ItemTypeModelForm
    success_url = reverse_lazy('itemtypes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "itemtype"
        return context


class ItemTypeUpdateView(UpdateView):
    model = ItemType
    template_name = 'generic_form.html'
    form_class = ItemTypeModelForm
    success_url = reverse_lazy('itemtypes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "itemtype"
        return context


class ItemTypeDeleteView(DeleteView):
    model = ItemType
    success_url = reverse_lazy('itemtypes')


# ItemWorkRelation views
class ItemWorkRelationTableView(ListView):
    model = ItemWorkRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return ItemWorkRelation.objects.filter(item__lot__collection__in=get_collections_for_session(self.request))

    def get_context_data(self, **kwargs):
        context = super(ItemWorkRelationTableView, self).get_context_data(**kwargs)
        filter = ItemWorkRelationFilter(self.request.GET, queryset=self.get_queryset())

        table = ItemWorkRelationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "itemworkrelation"
        context['add_url'] = reverse_lazy('add_itemworkrelation')

        return context


class ItemWorkRelationDetailView(PermissionRequiredMixin, DetailView):
    model = ItemWorkRelation
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check


class ItemWorkRelationCreateView(CreateView):
    model = ItemWorkRelation
    template_name = 'generic_form.html'
    form_class = ItemWorkRelationModelForm
    success_url = reverse_lazy('itemworkrelations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['items'] = Item.objects.filter(lot__collection__in=get_collections_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "itemworkrelation"
        return context


class ItemWorkRelationUpdateView(PermissionRequiredMixin, UpdateView):
    model = ItemWorkRelation
    template_name = 'generic_form.html'
    form_class = ItemWorkRelationModelForm
    success_url = reverse_lazy('itemworkrelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['items'] = Item.objects.filter(lot__collection__in=get_collections_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "itemworkrelation"
        return context


class ItemWorkRelationDeleteView(PermissionRequiredMixin, DeleteView):
    model = ItemWorkRelation

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class ItemWorkRelationAddView(PermissionRequiredMixin, UpdateView):
    """
    A view to add works to an item through ItemWorkRelations
    """
    model = Item
    template_name = 'items/manage_itemworkrelations_form.html'
    form_class = ItemWorkRelationAddForm

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().lot.collection.catalogue.first().dataset
    # End permission check

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']

    def get_context_data(self, **kwargs):
        context = super(ItemWorkRelationAddView, self).get_context_data(**kwargs)
        # print(self.object)

        context['existing_relations'] = [{'uuid': work.uuid, 'title': work.work.title} for work in self.object.works.all()]
        print(context['existing_relations'])

        context['form'] = ItemWorkRelationAddForm()
        print(str(context['form'].Media.js))
        context['form_as'] = 'table'  # Type of form
        context['js_variables'] = json.dumps({'viaf_select_id': ItemWorkRelationAddForm.viaf_select_id})

        context['action'] = _('Manage works for item')
        context['object_name'] = str(self.object)
        return context

    def post(self, request, *args, **kwargs):
        try:
            item = Item.objects.get(uuid=kwargs['pk'])

        except:
            import traceback
            traceback.print_exc()
            return HttpResponseRedirect(reverse_lazy('items'))

        work_id = request.POST[ItemWorkRelationAddForm.viaf_select_id]
        if work_id.startswith(ViafAPI.uri_base):
            get_work_args = {'viaf_id': work_id}
        else:
            get_work_args = {'pk': work_id}
        title = request.POST['title']

        try:
            work = Work.objects.get(**get_work_args)
        except:
            work = Work(viaf_id=work_id, title=title)
            work.save()

        try:
            itemworkrelation = ItemWorkRelation.objects.get(item=item, work=work)
            messages.add_message(self.request, messages.SUCCESS,
                                _("The work was already linked to this item."))
        except ObjectDoesNotExist as e:
            itemworkrelation = ItemWorkRelation(item=item, work=work)
            itemworkrelation.save()

        return HttpResponseRedirect(self.get_success_url())


# Language views
class LanguageTableView(ListView):
    model = Language
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Language.objects.all()

    def get_context_data(self, **kwargs):
        context = super(LanguageTableView, self).get_context_data(**kwargs)
        filter = LanguageFilter(self.request.GET, queryset=self.get_queryset())

        table = LanguageTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "language"
        context['add_url'] = reverse_lazy('add_language')

        return context


class LanguageDetailView(DetailView):
    model = Language


class LanguageCreateView(CreateView):
    model = Language
    template_name = 'generic_form.html'
    form_class = LanguageModelForm
    success_url = reverse_lazy('languages')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "language"
        return context


class LanguageUpdateView(UpdateView):
    model = Language
    template_name = 'generic_form.html'
    form_class = LanguageModelForm
    success_url = reverse_lazy('languages')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "language"
        return context


class LanguageDeleteView(DeleteView):
    model = Language
    success_url = reverse_lazy('languages')


# MaterialDetails views
class MaterialDetailsTableView(ListView):
    model = MaterialDetails
    template_name = 'generic_list.html'

    def get_queryset(self):
        return MaterialDetails.objects.all()

    def get_context_data(self, **kwargs):
        context = super(MaterialDetailsTableView, self).get_context_data(**kwargs)
        filter = MaterialDetailsFilter(self.request.GET, queryset=self.get_queryset())

        table = MaterialDetailsTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "materialdetail"
        context['add_url'] = reverse_lazy('add_materialdetails')

        return context


class MaterialDetailsDetailView(DetailView):
    model = MaterialDetails


class MaterialDetailsCreateView(CreateView):
    model = MaterialDetails
    template_name = 'generic_form.html'
    form_class = MaterialDetailsModelForm
    success_url = reverse_lazy('materialdetails')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "materialdetails"
        return context


class MaterialDetailsUpdateView(UpdateView):
    model = MaterialDetails
    template_name = 'generic_form.html'
    form_class = MaterialDetailsModelForm
    success_url = reverse_lazy('materialdetails')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "materialdetails"
        return context


class MaterialDetailsDeleteView(DeleteView):
    model = MaterialDetails
    success_url = reverse_lazy('materialdetails')


# PersonItemRelation views
class PersonItemRelationTableView(ListView):
    model = PersonItemRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return PersonItemRelation.objects.filter(item__lot__collection__in=get_collections_for_session(self.request))

    def get_context_data(self, **kwargs):
        context = super(PersonItemRelationTableView, self).get_context_data(**kwargs)
        filter = PersonItemRelationFilter(self.request.GET, queryset=self.get_queryset())

        table = PersonItemRelationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "personitemrelation"
        context['add_url'] = reverse_lazy('add_personitemrelation')

        return context


class PersonItemRelationDetailView(PermissionRequiredMixin, DetailView):
    model = PersonItemRelation
    template_name = 'generic_detail.html'

    # Object permission check by Django Guardian
    permission_required = 'catalogues.view_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check


class PersonItemRelationCreateView(CreateView):
    model = PersonItemRelation
    template_name = 'generic_form.html'
    form_class = PersonItemRelationModelForm
    success_url = reverse_lazy('personitemrelations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['items'] = Item.objects.filter(lot__collection__in=get_collections_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "personitemrelation"
        return context


class PersonItemRelationUpdateView(PermissionRequiredMixin, UpdateView):
    model = PersonItemRelation
    template_name = 'generic_form.html'
    form_class = PersonItemRelationModelForm
    success_url = reverse_lazy('personitemrelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['items'] = Item.objects.filter(lot__collection__in=get_collections_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "personitemrelation"
        return context


class PersonItemRelationDeleteView(PermissionRequiredMixin, DeleteView):
    model = PersonItemRelation
    success_url = reverse_lazy('personitemrelations')

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().item.lot.collection.catalogue.first().dataset
    # End permission check

    def get_success_url(self):
        if 'HTTP_REFERER' in self.request.META:
            return self.request.META['HTTP_REFERER']
        return self.success_url


@moderate(action=ModerationAction.CREATE)
class PersonItemRelationAddView(PermissionRequiredMixin, SingleObjectMixin, FormView):
    """
    A view to add persons to an item through PersonItemRelations
    """
    model = Item
    template_name = 'items/manage_personitemrelations_form.html'
    form_class = PersonItemRelationAddForm

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().lot.collection.catalogue.first().dataset
    # End permission check

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']

    def get_form(self):
        personitemrelation = PersonItemRelation(item=self.object)
        return self.form_class(instance=personitemrelation)

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super(PersonItemRelationAddView, self).get_context_data(**kwargs)

        context['existing_relations'] = [{'uuid': relation.uuid, 'person': relation.person, 'role': relation.role}
                                         for relation in self.object.personitemrelation_set.all()]

        # Add another Person
        context['addanother_person_form'] = PersonModelForm()
        context['js_variables'] = json.dumps({'viaf_select_id': PersonModelForm.suggest_select_ids})

        context['form_as'] = 'table'  # Type of form
        context['js_variables'] = json.dumps({})

        context['action'] = _('Manage people for item')

        context['object_name'] = str(self.object)
        return context

    def post(self, request, *args, **kwargs):
        personitemrelation = PersonItemRelation(item=self.get_object())
        form = PersonItemRelationAddForm(instance=personitemrelation, data=request.POST)
        if form.is_valid():
            form.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


def add_person_to_items(request):
    """
    Makes PersonItemRelations for a list of items
    :param request: 
    :return: 
    """
    if request.method == 'POST':
        if 'entries' in request.POST:
            items = request.POST.getlist('entries')
            for item_id in items:
                item = Item.objects.get(uuid=item_id)
                form_set = PersonItemRelationAddFormSet(data=request.POST)
                if form_set.is_valid() and 'change_dataset' in \
                        get_perms(request.user, item.lot.collection.catalogue.first().dataset):
                    for form in form_set:
                        if form.is_valid() and form.has_changed():
                            try:
                                personitemrelation = form.save(commit=False)
                                personitemrelation.item = item
                                personitemrelation.save()
                            except IntegrityError as ie:
                                # Probably a unique constraint error which means the relation already exists
                                messages.add_message(request, messages.ERROR,
                                                     _("{} is already {} of {}".format(form.cleaned_data['person'],
                                                                                       form.cleaned_data['role'], item)))
                else:
                    messages.add_message(request, messages.ERROR,
                                _("Item {} could not be used for adding a person.".format(item)))

        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        raise Http404

@require_POST
def set_publication_places_for_items(request):
    """
    Set the publication places (= Edition.place) for a list of items
    :param request:
    :return:
    """
    if 'entries' not in request.POST:
        messages.add_message(request, messages.WARNING, _("No items selected."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    item_ids = request.POST.getlist('entries')
    publicationplacesform = EditionPlacesForm(request.POST)

    if not publicationplacesform.is_valid():
        messages.add_message(request, messages.WARNING, _("The Places form was invalid."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    places = publicationplacesform.cleaned_data['publication_places']
    for item_id in item_ids:
        item = Item.objects.get(uuid=item_id)
        if 'change_dataset' not in get_perms(request.user, item.lot.collection.catalogue.first().dataset):
            messages.add_message(request, messages.ERROR,
                                 _("Item {} could not be used for setting places of publication"
                                   " because you are not allowed to change the dataset.".format(item)))
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        edition = item.edition
        if not edition:
            edition = Edition()
            item.edition = edition
            item.save()

        # Delete the publication places that are not linked to the given places
        PublicationPlace.objects.filter(edition=edition).exclude(place__in=places).delete()

        # Add publication places
        for place in places:
            try:
                PublicationPlace.objects.get_or_create(edition=edition, place=place)
            except IntegrityError as integrity_error:
                # Probably a duplicate entry
                pass

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def set_bookformat_for_items(request):
    """
    Set the book_format for a list of items
    :param request: 
    :return: 
    """
    if request.method == 'POST':
        if 'entries' in request.POST:
            items = request.POST.getlist('entries')
            itemformatform = ItemFormatForm(data=request.POST)
            if itemformatform.is_valid():
                for item_id in items:
                    item = Item.objects.get(uuid=item_id)
                    if 'change_dataset' in get_perms(request.user, item.lot.collection.catalogue.first().dataset):
                        item.book_format = itemformatform.cleaned_data['book_format']
                        item.save()
                    else:
                        messages.add_message(request, messages.ERROR,
                                             _("Item {} could not be used for setting a book format"
                                               " because you are not allowed to change the dataset.".format(item)))
            else:
                messages.add_message(request, messages.WARNING, _("The Book Format form was invalid."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        raise Http404


def set_publisher_for_items(request):
    """
    Set the publisher (= Edition.publisher) for a list of items
    :param request:
    :return:
    """
    if request.method == 'POST':
        if 'entries' in request.POST:
            items = request.POST.getlist('entries')
            publisherform = PublisherForm(data=request.POST)
            if publisherform.is_valid():
                for item_id in items:
                    item = Item.objects.get(uuid=item_id)
                    if 'change_dataset' in get_perms(request.user, item.lot.collection.catalogue.first().dataset):
                        if not item.edition:
                            item.edition = Edition()
                            item.save()
                        try:
                            publisher = Publisher(edition=item.edition, publisher=publisherform.cleaned_data['publisher'])
                            publisher.save()
                        except IntegrityError:
                            # Unique constraint failed; the Publisher already exists
                            pass
                    else:
                        messages.add_message(request, messages.ERROR,
                                             _("Item {} could not be used for setting a publisher"
                                               " because you are not allowed to change the dataset.".format(item)))
            else:
                messages.add_message(request, messages.WARNING, _("The Publisher form was invalid."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        raise Http404


def add_language_to_items(request):
    """
    Add language to a list of items
    :param request: 
    :return: 
    """
    if request.method == 'POST':
        if 'entries' in request.POST and 'language' in request.POST:
            items = request.POST.getlist('entries')
            languages = request.POST.getlist('language')
            for language_id in languages:
                language = Language.objects.get(uuid=language_id)
                for item_id in items:
                    item = Item.objects.get(uuid=item_id)
                    if 'change_dataset' in get_perms(request.user, item.lot.collection.catalogue.first().dataset):
                        try:
                            itemlanguagerelation = ItemLanguageRelation(item=item,
                                                                        language=language)
                            itemlanguagerelation.save()
                        except IntegrityError:
                            # Unique constraint failed; the ItemLanguageRelation already exists
                            pass
                    else:
                        messages.add_message(request, messages.ERROR,
                                             _("Item {} could not be used for adding a language"
                                               " because you are not allowed to change the dataset.".format(item)))
        else:
            messages.add_message(request, messages.WARNING, _("No items and/or no language selected."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        raise Http404


def add_type_to_items(request):
    """
    Add type to a list of items
    :param request: 
    :return: 
    """
    if request.method == 'POST':
        if 'entries' in request.POST and 'type' in request.POST:
            items = request.POST.getlist('entries')
            types = request.POST.getlist('type')
            for type_id in types:
                itemtype = ItemType.objects.get(uuid=type_id)
                for item_id in items:
                    item = Item.objects.get(uuid=item_id)
                    if 'change_dataset' in get_perms(request.user, item.lot.collection.catalogue.first().dataset):
                        try:
                            itemitemtyperelation = ItemItemTypeRelation(item=item, type=itemtype)
                            itemitemtyperelation.save()
                        except IntegrityError:
                            # Unique constraint failed; the ItemItemTypeRelation already exists
                            pass
                    else:
                        messages.add_message(request, messages.ERROR,
                                             _("Item {} could not be used for adding a type"
                                               " because you are not allowed to change the dataset.".format(item)))
        else:
            messages.add_message(request, messages.WARNING, _("No items and/or no types selected."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        raise Http404


def add_tags_to_items(request):
    """
    Add tags to a list of items
    :param request:
    :return:
    """
    if request.method == 'POST':
        if 'entries' in request.POST and 'tag' in request.POST:
            items = request.POST.getlist('entries')
            tags = request.POST.getlist('tag')
            for tag_id in tags:
                tag = Tag.objects.get(id=tag_id)
                for item_id in items:
                    item = Item.objects.get(uuid=item_id)
                    if 'change_dataset' in get_perms(request.user, item.lot.collection.catalogue.first().dataset):
                        try:
                            if tag.id not in item.tags.values_list('tag', flat=True):
                                item.tags.create(tag=tag)
                        except IntegrityError as ie:
                            # Unique constraint failed; the ItemItemTypeRelation already exists
                            print(ie)
                            pass
                    else:
                        messages.add_message(request, messages.ERROR,
                                             _("Item {} could not be used for adding a tag"
                                               " because you are not allowed to change the dataset.".format(item)))
        else:
            messages.add_message(request, messages.WARNING, _("No items and/or no tags selected."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        raise Http404


def add_works_to_items(request):
    """
    Add works to a list of items
    :param request: 
    :return: 
    """
    if request.method == 'POST':
        if 'entries' in request.POST and 'work' in request.POST:
            items = request.POST.getlist('entries')
            works = request.POST.getlist('work')
            for work_id in works:
                work = Work.objects.get(uuid=work_id)
                for item_id in items:
                    item = Item.objects.get(uuid=item_id)
                    if 'change_dataset' in get_perms(request.user, item.lot.collection.catalogue.first().dataset):
                        try:
                            ItemWorkRelation.objects.create(item=item, work=work)
                        except IntegrityError:
                            # Unique constraint failed; the ItemItemTypeRelation already exists
                            pass
                    else:
                        messages.add_message(request, messages.ERROR,
                                             _("Item {} could not be used for adding a work"
                                               " because you are not allowed to change the dataset.".format(item)))
        else:
            messages.add_message(request, messages.WARNING, _("No items and/or no works selected."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        raise Http404


def add_materialdetails_to_items(request):
    """
    Add Material_details to a list of items
    :param request:
    :return:
    """
    if request.method == 'POST':
        if 'entries' in request.POST and 'material_details' in request.POST:
            items = request.POST.getlist('entries')
            material_details_objects = request.POST.getlist('material_details')
            for material_details_id in material_details_objects:
                material_details = MaterialDetails.objects.get(uuid=material_details_id)
                for item_id in items:
                    item = Item.objects.get(uuid=item_id)
                    if 'change_dataset' in get_perms(request.user, item.lot.collection.catalogue.first().dataset):
                        try:
                            ItemMaterialDetailsRelation.objects.create(item=item, material_details=material_details)
                        except IntegrityError:
                            # Unique constraint failed; the ItemItemTypeRelation already exists
                            pass
                    else:
                        messages.add_message(request, messages.ERROR,
                                             _("Item {} could not be used for adding material details"
                                               " because you are not allowed to change the dataset.".format(item)))
        else:
            messages.add_message(request, messages.WARNING, _("No items and/or no material details selected."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        raise Http404


def add_parisian_category_to_items(request):
    """
    Add ParisianCategories to a list of items
    :param request:
    :return:
    """
    if request.method == 'POST':
        if 'entries' in request.POST and 'parisian_category' in request.POST:
            item_ids = request.POST.getlist('entries')
            items = Item.objects.filter(uuid__in=item_ids, lot__collection__in=get_collections_for_session(request))
            if len(item_ids) != items.count():
                messages.add_message(request, messages.ERROR,
                                     _("Some items could not be used for adding a parisian category"
                                       " because you are not allowed to change the dataset."))
            parisian_category_id = request.POST.get('parisian_category')
            items.update(parisian_category_id=parisian_category_id)
        else:
            messages.add_message(request, messages.WARNING, _("No items and/or no Parisian categories selected."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        raise Http404
    
    
def toggle_uncountable_book_items(request):
    """
    Toggle the uncountable_book_items
    :param request: 
    :return: 
    """
    # POST only
    if request.method != 'POST':
        raise Http404

    # Check that *entries* are there
    if 'entries' not in request.POST:
        messages.add_message(request, messages.WARNING, _("No items selected."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    item_ids = request.POST.getlist('entries')
    items = Item.objects.filter(uuid__in=item_ids, lot__collection__in=get_collections_for_session(request))
    if len(item_ids) != items.count():
        messages.add_message(request, messages.ERROR, _("Some items could not be used for toggling uncountable book"
                                                        " items because you are not allowed to change the dataset."))
    items.update(uncountable_book_items=Case(When(uncountable_book_items=True, then=False), default=True))
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def set_publication_place_for_editions(request):
    """
    Set the publication place for a list of editions
    :param request:
    :return:
    """
    if request.method == 'POST':
        if 'entries' in request.POST:
            editions = request.POST.getlist('entries')
            publicationplaceform = EditionPlaceForm(data=request.POST)
            if publicationplaceform.is_valid():
                for edition_id in editions:
                    edition = Edition.objects.get(uuid=edition_id)
                    edition.place = publicationplaceform.cleaned_data['place']
                    edition.save()
            else:
                messages.add_message(request, messages.WARNING, _("The Place form was invalid."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        raise Http404


def set_publisher_for_editions(request):
    """
    Set the publisher for a list of editions
    :param request:
    :return:
    """
    if request.method == 'POST':
        print(1)
        print(request.POST)
        if 'entries' in request.POST:
            print(2)
            editions = request.POST.getlist('entries')
            publisherform = PublisherForm(data=request.POST)
            if publisherform.is_valid():
                print(3)
                for edition_id in editions:
                    edition = Edition.objects.get(uuid=edition_id)
                    try:
                        publisher = Publisher(edition=edition, publisher=publisherform.cleaned_data['publisher'])
                        publisher.save()
                    except IntegrityError:
                        # Unique constraint failed; the Publisher already exists
                        pass
            else:
                messages.add_message(request, messages.WARNING, _("The Publisher form was invalid."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        raise Http404


# PersonItemRelationRole views
class PersonItemRelationRoleTableView(ListView):
    model = PersonItemRelationRole
    template_name = 'generic_list.html'

    def get_queryset(self):
        return PersonItemRelationRole.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PersonItemRelationRoleTableView, self).get_context_data(**kwargs)
        filter = PersonItemRelationRoleFilter(self.request.GET, queryset=self.get_queryset())

        table = PersonItemRelationRoleTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "personitemrelationrole"
        context['add_url'] = reverse_lazy('add_personitemrelationrole')

        return context


class PersonItemRelationRoleDetailView(DetailView):
    model = PersonItemRelationRole


class PersonItemRelationRoleCreateView(CreateView):
    model = PersonItemRelationRole
    template_name = 'generic_form.html'
    form_class = PersonItemRelationRoleModelForm
    success_url = reverse_lazy('personitemrelationroles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "personitemrelationrole"
        return context


class PersonItemRelationRoleUpdateView(UpdateView):
    model = PersonItemRelationRole
    template_name = 'generic_form.html'
    form_class = PersonItemRelationRoleModelForm
    success_url = reverse_lazy('personitemrelationroles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "personitemrelationrole"
        return context


class PersonItemRelationRoleDeleteView(DeleteView):
    model = PersonItemRelationRole
    success_url = reverse_lazy('personitemrelationroles')


# Edition views
class EditionTableView(ListView):
    model = Edition
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Edition.objects.all()

    def get_context_data(self, **kwargs):
        context = super(EditionTableView, self).get_context_data(**kwargs)
        filter = EditionFilter(self.request.GET, queryset=self.get_queryset())

        table = EditionTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "edition"
        context['add_url'] = reverse_lazy('add_edition')
        context['batch_edit_options'] = [
            {
                'id': 'set_editionplace',
                'label': _("Set publication place"),
                'url': reverse_lazy('set_editionplace_for_editions'),
                'form': EditionPlaceForm
            },
            {
                'id': 'set_publisher',
                'label': _("Set publisher"),
                'url': reverse_lazy('set_publisher_for_editions'),
                'form': PublisherForm
            },
        ]

        return context


class EditionRankingTableView(ListView):
    model = Edition
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Edition.objects.all()

    def get_context_data(self, **kwargs):
        context = super(EditionRankingTableView, self).get_context_data(**kwargs)
        filter = EditionRankingFilter(self.request.GET, queryset=self.get_queryset(), request=self.request)

        table = EditionRankingTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name_plural'] = "Edition ranking"
        context['add_url'] = reverse_lazy('add_edition')

        return context


class EditionDetailView(GenericDetailView):
    model = Edition
    object_fields = ['year_start', 'year_end', 'year_tag', 'terminus_post_quem', 'place', 'url']


class EditionCreateView(CreateView):
    model = Edition
    template_name = 'generic_form.html'
    form_class = EditionModelForm
    success_url = reverse_lazy('editions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "edition"
        return context


class EditionUpdateView(View):
    def get(self, request, **kwargs):
        obj = get_object_or_404(Edition, pk=kwargs['pk'])
        if obj.items.count() != 1:
            messages.add_message(request, messages.WARNING,
                             _("Edition ({}) does not have exactly one item.".format(obj)))
            return HttpResponseRedirect(self.request.META['HTTP_REFERER'])
        return HttpResponseRedirect(reverse_lazy('change_item', kwargs={'pk': obj.items.all()[0].uuid}))


class EditionDeleteView(DeleteView):
    model = Edition
    success_url = reverse_lazy('editions')


# Publisher views
class PublisherTableView(ListView):
    model = Publisher
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Publisher.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PublisherTableView, self).get_context_data(**kwargs)
        filter = PublisherFilter(self.request.GET, queryset=self.get_queryset())

        table = PublisherTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "publisher"
        context['add_url'] = reverse_lazy('add_publisher')

        return context


class PublisherDetailView(DetailView):
    model = Publisher


class PublisherCreateView(CreateView):
    model = Publisher
    template_name = 'generic_form.html'
    form_class = PublisherModelForm
    success_url = reverse_lazy('publishers')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "publisher"
        return context


class PublisherUpdateView(UpdateView):
    model = Publisher
    template_name = 'generic_form.html'
    form_class = PublisherModelForm
    success_url = reverse_lazy('publishers')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "publisher"
        return context


class PublisherDeleteView(DeleteView):
    model = Publisher
    success_url = reverse_lazy('publishers')


# Subject views
class SubjectTableView(ListView):
    model = Subject
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Subject.objects.all()

    def get_context_data(self, **kwargs):
        context = super(SubjectTableView, self).get_context_data(**kwargs)
        filter = SubjectFilter(self.request.GET, queryset=self.get_queryset())

        table = SubjectTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "subject"
        context['add_url'] = reverse_lazy('add_subject')

        return context


class SubjectDetailView(DetailView):
    model = Subject


class SubjectCreateView(CreateView):
    model = Subject
    template_name = 'generic_form.html'
    form_class = SubjectModelForm
    success_url = reverse_lazy('subjects')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "subject"
        return context


class SubjectUpdateView(UpdateView):
    model = Subject
    template_name = 'generic_form.html'
    form_class = SubjectModelForm
    success_url = reverse_lazy('subjects')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "subject"
        return context


class SubjectDeleteView(DeleteView):
    model = Subject
    success_url = reverse_lazy('subjects')


# Work views
class WorkTableView(ListView):
    model = Work
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Work.objects.filter(items__item__lot__collection_id__in=get_collections_for_session(self.request))\
            .distinct()

    def get_context_data(self, **kwargs):
        datasets_permitted = get_permitted_datasets_for_session(self.request)

        context = super(WorkTableView, self).get_context_data(**kwargs)
        filter = WorkFilter(self.request.GET, queryset=self.get_queryset())

        table = WorkTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)
        if not datasets_permitted:
            table.exclude = ('checkbox')

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "work"
        context['add_url'] = reverse_lazy('add_work') if datasets_permitted else None
        context['batch_edit_options'] = [
            {
                'id': 'add_parisiancategories',
                'label': _("Add Parisian categories"),
                'url': reverse_lazy('add_parisiancategories_to_items_of_works'),
                'form': ItemParisianCategoriesForm
            },
        ] if datasets_permitted else None

        return context


def add_parisiancategories_to_items_of_works(request):
    """
    Add ParisianCategories to items linked to a list of works
    :param request:
    :return:
    """
    if request.method == 'POST':
        if 'entries' in request.POST and 'parisian_category' in request.POST:
            work_ids = request.POST.getlist('entries')
            items = Item.objects.filter(works__work_id__in=work_ids,
                                        lot__collection__in=get_collections_for_session(request))
            parisian_category_id = request.POST.get('parisian_category')
            items.update(parisian_category_id=parisian_category_id)
        else:
            messages.add_message(request, messages.WARNING, _("No items and/or no Parisian categories selected."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        raise Http404


class WorkRankingTableView(ListView):
    model = Work
    template_name = 'generic_list.html'
    filter_class = WorkRankingFilter
    table_class = WorkRankingTable

    def get_queryset(self):
        return Work.objects.all()

    def get_context_data(self, **kwargs):
        datasets_permitted = get_permitted_datasets_for_session(self.request)

        context = super(WorkRankingTableView, self).get_context_data(**kwargs)
        filter = self.filter_class(self.request.GET, queryset=self.get_queryset(), request=self.request)

        table = self.table_class(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "work"
        context['add_url'] = reverse_lazy('add_work') if datasets_permitted else None

        return context


class WorkWeightedRankingTableView(WorkRankingTableView):
    filter_class = WorkWeightedRankingFilter
    table_class = WorkWeightedRankingTable

    def get(self, request):
        datasets = get_datasets_for_session(request)
        if len(datasets) == 1 and datasets[0].name == settings.DATASET_NAME_FOR_ANONYMOUSUSER:
            return super().get(request)
        messages.error(request, f"Select only dataset {settings.DATASET_NAME_FOR_ANONYMOUSUSER} to view this page.")
        return render(request, 'warning.html', {})


class WorkDetailView(GenericDetailView):
    model = Work
    object_fields = ['title', 'viaf_id']


class WorkCreateView(CreateView):
    model = Work
    template_name = 'generic_form.html'
    form_class = WorkModelForm
    success_url = reverse_lazy('works')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "work"
        context['js_variables'] = json.dumps({'viaf_selec_id': 'viaf_id'})
        return context


class WorkUpdateView(UpdateView):
    model = Work
    template_name = 'generic_form.html'
    form_class = WorkModelForm
    success_url = reverse_lazy('works')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "work"
        return context


class WorkDeleteView(DeleteView):
    model = Work
    success_url = reverse_lazy('works')


# WorkAuthor views
class WorkAuthorTableView(ListView):
    model = WorkAuthor
    template_name = 'generic_list.html'

    def get_queryset(self):
        return WorkAuthor.objects.all()

    def get_context_data(self, **kwargs):
        context = super(WorkAuthorTableView, self).get_context_data(**kwargs)
        filter = WorkAuthorFilter(self.request.GET, queryset=self.get_queryset())

        table = WorkAuthorTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "workauthor"
        context['add_url'] = reverse_lazy('add_workauthor')

        return context


class WorkAuthorDetailView(DetailView):
    model = WorkAuthor


class WorkAuthorCreateView(CreateView):
    model = WorkAuthor
    template_name = 'generic_form.html'
    form_class = WorkAuthorModelForm
    success_url = reverse_lazy('workauthors')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "workauthor"
        return context


class WorkAuthorUpdateView(UpdateView):
    model = WorkAuthor
    template_name = 'generic_form.html'
    form_class = WorkAuthorModelForm
    success_url = reverse_lazy('workauthors')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "workauthor"
        return context


class WorkAuthorDeleteView(DeleteView):
    model = WorkAuthor
    success_url = reverse_lazy('workauthors')


# WorkSubject views
class WorkSubjectTableView(ListView):
    model = WorkSubject
    template_name = 'generic_list.html'

    def get_queryset(self):
        return WorkSubject.objects.all()

    def get_context_data(self, **kwargs):
        context = super(WorkSubjectTableView, self).get_context_data(**kwargs)
        filter = WorkSubjectFilter(self.request.GET, queryset=self.get_queryset())

        table = WorkSubjectTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "worksubject"
        context['add_url'] = reverse_lazy('add_worksubject')

        return context


class WorkSubjectDetailView(DetailView):
    model = WorkSubject


class WorkSubjectCreateView(CreateView):
    model = WorkSubject
    template_name = 'generic_form.html'
    form_class = WorkSubjectModelForm
    success_url = reverse_lazy('worksubjects')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "worksubject"
        return context


class WorkSubjectUpdateView(UpdateView):
    model = WorkSubject
    template_name = 'generic_form.html'
    form_class = WorkSubjectModelForm
    success_url = reverse_lazy('worksubjects')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "worksubject"
        return context


class WorkSubjectDeleteView(DeleteView):
    model = WorkSubject
    success_url = reverse_lazy('worksubjects')


class ItemAndEditionCreateView(CreateView):
    form_class = ItemAndEditionForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('items')
    success_msg = _("Added an item and a edition.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['catalogues'] = Catalogue.objects.filter(dataset__in=get_datasets_for_session(self.request))
        kwargs['lots'] = Lot.objects.filter(collection__in=get_collections_for_session(self.request))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "item and edition"
        return context

    @transaction.atomic
    def form_valid(self, form):
        # Save the edition first, because the item needs a edition before it
        # can be saved.
        edition = form['edition'].save()
        item = form['item'].save(commit=False)
        item.edition = edition
        item.save()

        # Because Item form was not saved (commit=False)
        form['item'].save_tags()
        form['item'].save_languages()
        form['item'].save_publishers()
        form['item'].save_material_details()
        form['item'].save_itemtypes()

        messages.add_message(self.request, messages.SUCCESS, self.success_msg)
        return HttpResponseRedirect(self.success_url)


class ItemAndEditionUpdateView(PermissionRequiredMixin, ItemAndEditionCreateView):
    model = Item
    template_name = 'items/item_update_form.html'
    success_msg = _("Changed an item and a edition.")

    # Object permission check by Django Guardian
    permission_required = 'catalogues.change_dataset'

    def get_permission_object(self):
        return self.get_object().lot.collection.catalogue.first().dataset
    # End permission check

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        return context

    def get_form_kwargs(self):
        kwargs = super(ItemAndEditionUpdateView, self).get_form_kwargs()
        self.object = self.get_object()
        kwargs.update(instance={
            'item': self.object,
            'edition': self.object.edition,
        })
        kwargs['catalogues'] = Catalogue.objects.filter(dataset__in=get_datasets_for_session(self.request))
        kwargs['lots'] = Lot.objects.filter(collection__in=get_collections_for_session(self.request))
        return kwargs
