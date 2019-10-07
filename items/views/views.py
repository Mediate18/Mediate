from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.forms import formset_factory
from django_tables2.config import RequestConfig
from django_tables2.export.export import TableExport

from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from django.shortcuts import get_object_or_404
import django_tables2
from guardian.shortcuts import get_objects_for_user

from dal import autocomplete
from django.http import JsonResponse
import re
import json


from ..forms import *
from ..filters import *
from ..tables import *

from persons.forms import PersonModelForm
from mediate.views import GenericDetailView
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
        items = Item.objects.all()
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
        context = super(ItemTableView, self).get_context_data(**kwargs)
        filter = ItemFilter(self.request.GET, queryset=self.get_queryset())

        table = ItemTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "item"
        context['add_url'] = reverse_lazy('add_item')
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
                'id': 'set_editionplace',
                'label': _("Set publication place"),
                'url': reverse_lazy('set_editionplace'),
                'form': EditionPlaceForm
            },
            {
                'id': 'set_publisher',
                'label': _("Set publisher"),
                'url': reverse_lazy('set_publisher'),
                'form': PublisherForm
            },
            {
                'id': 'set_bookformat',
                'label': _("Set book format"),
                'url': reverse_lazy('set_bookformat'),
                'form': ItemFormatForm
            }
        ]

        return context


class TaggedItemTableView(ListView):
    model = Item
    template_name = 'generic_list.html'

    def get_queryset(self):
        tags = get_objects_for_user(self.request.user, 'tagme.view_entities_with_this_tag')
        return Item.objects.filter(tags__tag__in=tags)

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


class ItemLocationMapView(ListView):
    model = Item
    template_name = 'generic_location_map.html'

    def get_queryset(self):
        items = Item.objects.filter(edition__place__latitude__isnull=False, edition__place__longitude__isnull=False)
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

        return context


class ItemDetailView(DetailView):
    model = Item
    template_name = 'items/item_detail.html'


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


@moderate(action=ModerationAction.UPDATE)
class ItemUpdateView(UpdateView):
    model = Item
    template_name = 'generic_form.html'
    form_class = ItemModelForm
    success_url = reverse_lazy('items')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "item"
        return context


class ItemDeleteView(DeleteView):
    model = Item
    success_url = reverse_lazy('items')


# ItemAuthor views
class ItemAuthorTableView(ListView):
    model = ItemAuthor
    template_name = 'generic_list.html'

    def get_queryset(self):
        return ItemAuthor.objects.all()

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


class ItemAuthorDetailView(DetailView):
    model = ItemAuthor


class ItemAuthorCreateView(CreateView):
    model = ItemAuthor
    template_name = 'generic_form.html'
    form_class = ItemAuthorModelForm
    success_url = reverse_lazy('itemauthors')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "itemauthor"
        return context


class ItemAuthorUpdateView(UpdateView):
    model = ItemAuthor
    template_name = 'generic_form.html'
    form_class = ItemAuthorModelForm
    success_url = reverse_lazy('itemauthors')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "itemauthor"
        return context


class ItemAuthorDeleteView(DeleteView):
    model = ItemAuthor
    success_url = reverse_lazy('itemauthors')


# ItemItemTypeRelation views
class ItemItemTypeRelationTableView(ListView):
    model = ItemItemTypeRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return ItemItemTypeRelation.objects.all()

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


class ItemItemTypeRelationDetailView(DetailView):
    model = ItemItemTypeRelation


class ItemItemTypeRelationCreateView(CreateView):
    model = ItemItemTypeRelation
    template_name = 'generic_form.html'
    form_class = ItemItemTypeRelationModelForm
    success_url = reverse_lazy('itemitemtyperelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "itemitemtyperelation"
        return context


class ItemItemTypeRelationUpdateView(UpdateView):
    model = ItemItemTypeRelation
    template_name = 'generic_form.html'
    form_class = ItemItemTypeRelationModelForm
    success_url = reverse_lazy('itemitemtyperelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "itemitemtyperelation"
        return context


class ItemItemTypeRelationDeleteView(DeleteView):
    model = ItemItemTypeRelation
    success_url = reverse_lazy('itemitemtyperelations')


# ItemLanguageRelation views
class ItemLanguageRelationTableView(ListView):
    model = ItemLanguageRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return ItemLanguageRelation.objects.all()

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


class ItemLanguageRelationDetailView(DetailView):
    model = ItemLanguageRelation


class ItemLanguageRelationCreateView(CreateView):
    model = ItemLanguageRelation
    template_name = 'generic_form.html'
    form_class = ItemLanguageRelationModelForm
    success_url = reverse_lazy('itemlanguagerelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "itemlanguagerelation"
        return context


class ItemLanguageRelationUpdateView(UpdateView):
    model = ItemLanguageRelation
    template_name = 'generic_form.html'
    form_class = ItemLanguageRelationModelForm
    success_url = reverse_lazy('itemlanguagerelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "itemlanguagerelation"
        return context


class ItemLanguageRelationDeleteView(DeleteView):
    model = ItemLanguageRelation
    success_url = reverse_lazy('itemlanguagerelations')


# ItemMaterialDetailsRelation views
class ItemMaterialDetailsRelationTableView(ListView):
    model = ItemMaterialDetailsRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return ItemMaterialDetailsRelation.objects.all()

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


class ItemMaterialDetailsRelationDetailView(DetailView):
    model = ItemMaterialDetailsRelation


class ItemMaterialDetailsRelationCreateView(CreateView):
    model = ItemMaterialDetailsRelation
    template_name = 'generic_form.html'
    form_class = ItemMaterialDetailsRelationModelForm
    success_url = reverse_lazy('itemmaterialdetailsrelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "itemmaterialdetailsrelation"
        return context


class ItemMaterialDetailsRelationUpdateView(UpdateView):
    model = ItemMaterialDetailsRelation
    template_name = 'generic_form.html'
    form_class = ItemMaterialDetailsRelationModelForm
    success_url = reverse_lazy('itemmaterialdetailsrelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "itemmaterialdetailsrelation"
        return context


class ItemMaterialDetailsRelationDeleteView(DeleteView):
    model = ItemMaterialDetailsRelation
    success_url = reverse_lazy('itemmaterialdetailsrelations')


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
        return ItemWorkRelation.objects.all()

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


class ItemWorkRelationDetailView(DetailView):
    model = ItemWorkRelation


class ItemWorkRelationCreateView(CreateView):
    model = ItemWorkRelation
    template_name = 'generic_form.html'
    form_class = ItemWorkRelationModelForm
    success_url = reverse_lazy('itemworkrelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "itemworkrelation"
        return context


class ItemWorkRelationUpdateView(UpdateView):
    model = ItemWorkRelation
    template_name = 'generic_form.html'
    form_class = ItemWorkRelationModelForm
    success_url = reverse_lazy('itemworkrelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "itemworkrelation"
        return context


class ItemWorkRelationDeleteView(DeleteView):
    model = ItemWorkRelation

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class VIAFSuggest(autocomplete.Select2ListView):
    def get(self, request, *args, **kwargs):
        return self.find_viaf(self.q)

    @staticmethod
    def find_viaf(q, discard_viaf_ids=set(), json_output=True, cql_relation='cql.any'):
        viaf = ViafAPI()
        viaf_result_raw = viaf.search('%s = "%s"' % (cql_relation, q)) or []
        viaf_result = [dict(
            id=item.uri,
            id_number=item.viaf_id,
            text=escape(item.label),
            nametype=item.nametype,
            class_name="viaf_api",
            external_url=item.uri,
            clean_text=escape(item.label)
        ) for item in viaf_result_raw if item.viaf_id not in discard_viaf_ids]

        if json_output:
            return JsonResponse({
                'results': viaf_result
            })
        else:
            return viaf_result


class WorkAndVIAFSuggest(autocomplete.Select2ListView):
    def get(self, request, *args, **kwargs):
        work_result_raw = Work.objects.filter(title__icontains=self.q)
        work_viaf_ids = set()
        work_result = []
        for obj in work_result_raw:

            obj_dict = dict(
                id=obj.pk,
                id_number=obj.pk,
                text='<i>'+escape(obj.title)+'</i>',
                nametype='',
                class_name="local_work",
                external_url=obj.viaf_id,
                clean_text=escape(obj.title)
            )
            work_result.append(obj_dict)

            if obj.viaf_id:
                id_number = re.match(r'.*?(\d+)$', obj.viaf_id).group(1)
                work_viaf_ids.add(id_number)

        viaf_result = VIAFSuggest.find_viaf(self.q, discard_viaf_ids=work_viaf_ids, json_output=False,
                                            cql_relation='local.uniformTitleWorks')

        return JsonResponse({'results': work_result + viaf_result})


class PersonVIAFSuggest(autocomplete.Select2ListView):
    def get(self, request, *args, **kwargs):
        viaf_result = VIAFSuggest.find_viaf(self.q, json_output=False, cql_relation='local.personalNames')

        return JsonResponse({'results': viaf_result})


class WorkVIAFSuggest(autocomplete.Select2ListView):
    def get(self, request, *args, **kwargs):
        viaf_result = VIAFSuggest.find_viaf(self.q, json_output=False, cql_relation='local.uniformTitleWorks')

        return JsonResponse({'results': viaf_result})


class ItemWorkRelationAddView(UpdateView):
    """
    A view to add works to an item through ItemWorkRelations
    """
    model = Item
    template_name = 'items/manage_itemworkrelations_form.html'
    form_class = ItemWorkRelationAddForm

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
        return PersonItemRelation.objects.all()

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


class PersonItemRelationDetailView(DetailView):
    model = PersonItemRelation


class PersonItemRelationCreateView(CreateView):
    model = PersonItemRelation
    template_name = 'generic_form.html'
    form_class = PersonItemRelationModelForm
    success_url = reverse_lazy('personitemrelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "personitemrelation"
        return context


class PersonItemRelationUpdateView(UpdateView):
    model = PersonItemRelation
    template_name = 'generic_form.html'
    form_class = PersonItemRelationModelForm
    success_url = reverse_lazy('personitemrelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "personitemrelation"
        return context


class PersonItemRelationDeleteView(DeleteView):
    model = PersonItemRelation
    success_url = reverse_lazy('personitemrelations')

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


@moderate(action=ModerationAction.CREATE)
class PersonItemRelationAddView(SingleObjectMixin, FormView):
    """
    A view to add persons to an item through PersonItemRelations
    """
    model = Item
    template_name = 'items/manage_personitemrelations_form.html'
    form_class = PersonItemRelationAddForm

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
        if 'items' in request.POST:
            items = request.POST.getlist('items')
            for item_id in items:
                item = Item.objects.get(uuid=item_id)
                form_set = PersonItemRelationAddFormSet(data=request.POST)
                if form_set.is_valid():
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


def set_publication_place_for_items(request):
    """
    Set the publication place (= Edition.place) for a list of items
    :param request:
    :return:
    """
    if request.method == 'POST':
        if 'items' in request.POST:
            items = request.POST.getlist('items')
            publicationplaceform = EditionPlaceForm(data=request.POST)
            if publicationplaceform.is_valid():
                for item_id in items:
                    item = Item.objects.get(uuid=item_id)
                    if not item.edition:
                        item.edition = Edition()
                        item.save()
                    item.edition.place = publicationplaceform.cleaned_data['place']
                    item.edition.save()
            else:
                messages.add_message(request, messages.WARNING, _("The Place form was invalid."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        raise Http404


def set_bookformat_for_items(request):
    """
    Set the book_format for a list of items
    :param request: 
    :return: 
    """
    if request.method == 'POST':
        if 'items' in request.POST:
            items = request.POST.getlist('items')
            itemformatform = ItemFormatForm(data=request.POST)
            if itemformatform.is_valid():
                for item_id in items:
                    item = Item.objects.get(uuid=item_id)
                    item.book_format = itemformatform.cleaned_data['book_format']
                    item.save()
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
        if 'items' in request.POST:
            items = request.POST.getlist('items')
            publisherform = PublisherForm(data=request.POST)
            if publisherform.is_valid():
                for item_id in items:
                    item = Item.objects.get(uuid=item_id)
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

        return context


class EditionDetailView(GenericDetailView):
    model = Edition
    object_fields = ['year', 'year_tag', 'terminus_post_quem', 'place', 'url']


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
        if obj.items.count() is not 1:
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
        return Work.objects.all()

    def get_context_data(self, **kwargs):
        context = super(WorkTableView, self).get_context_data(**kwargs)
        filter = WorkFilter(self.request.GET, queryset=self.get_queryset())

        table = WorkTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "work"
        context['add_url'] = reverse_lazy('add_work')

        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "item and edition"
        return context

    def form_valid(self, form):
        # Save the edition first, because the item needs a edition before it
        # can be saved.
        edition = form['edition'].save()
        item = form['item'].save(commit=False)
        item.edition = edition
        item.save()
        messages.add_message(self.request, messages.SUCCESS,
                             _("Added an item and a edition."))
        return HttpResponseRedirect(self.success_url)


class ItemAndEditionUpdateView(ItemAndEditionCreateView):
    model = Item

    def get_form_kwargs(self):
        kwargs = super(ItemAndEditionUpdateView, self).get_form_kwargs()
        self.object = self.get_object()
        kwargs.update(instance={
            'item': self.object,
            'edition': self.object.edition,
        })
        return kwargs
