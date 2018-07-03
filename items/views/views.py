from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.forms.models import inlineformset_factory
from django.core.exceptions import ObjectDoesNotExist

from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
import django_tables2

from dal import autocomplete
from django.http import JsonResponse
import requests
import re
import json

from viapy.api import ViafAPI

from ..forms import *
from ..filters import *
from ..tables import *

from persons.forms import PersonModelForm


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class BookFormatDeleteView(DeleteView):
    model = BookFormat
    success_url = reverse_lazy('bookformats')


# Item views
class ItemTableView(ListView):
    model = Item
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Item.objects.all()

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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class ItemAuthorDeleteView(DeleteView):
    model = ItemAuthor
    success_url = reverse_lazy('itemauthors')


# ItemBookFormatRelation views
class ItemBookFormatRelationTableView(ListView):
    model = ItemBookFormatRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return ItemBookFormatRelation.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ItemBookFormatRelationTableView, self).get_context_data(**kwargs)
        filter = ItemBookFormatRelationFilter(self.request.GET, queryset=self.get_queryset())

        table = ItemBookFormatRelationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "itembookformatrelation"
        context['add_url'] = reverse_lazy('add_itembookformatrelation')

        return context


class ItemBookFormatRelationDetailView(DetailView):
    model = ItemBookFormatRelation


class ItemBookFormatRelationCreateView(CreateView):
    model = ItemBookFormatRelation
    template_name = 'generic_form.html'
    form_class = ItemBookFormatRelationModelForm
    success_url = reverse_lazy('itembookformatrelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "itembookformatrelation"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class ItemBookFormatRelationUpdateView(UpdateView):
    model = ItemBookFormatRelation
    template_name = 'generic_form.html'
    form_class = ItemBookFormatRelationModelForm
    success_url = reverse_lazy('itembookformatrelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "itembookformatrelation"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class ItemBookFormatRelationDeleteView(DeleteView):
    model = ItemBookFormatRelation
    success_url = reverse_lazy('itembookformatrelations')


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class PersonItemRelationDeleteView(DeleteView):
    model = PersonItemRelation
    success_url = reverse_lazy('personitemrelations')

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class PersonItemRelationAddView(UpdateView):
    """
    A view to add persons to an item through PersonItemRelations
    """
    model = Item
    template_name = 'items/manage_personitemrelations_form.html'
    form_class = PersonItemRelationAddForm

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']

    def get_context_data(self, **kwargs):
        context = super(PersonItemRelationAddView, self).get_context_data(**kwargs)
        # print(self.object)

        context['existing_relations'] = [{'uuid': relation.uuid, 'person': relation.person, 'role': relation.role}
                                         for relation in self.object.personitemrelation_set.all()]
        print(context['existing_relations'])

        context['form'] = PersonItemRelationAddForm()

        # Add another Person
        context['addanother_person_form'] = PersonModelForm()
        context['js_variables'] = json.dumps({'viaf_select_id': PersonModelForm.cerl_select_id})

        context['form_as'] = 'table'  # Type of form
        context['js_variables'] = json.dumps({})

        context['action'] = _('Manage people for item')

        context['object_name'] = str(self.object)
        return context

    def post(self, request, *args, **kwargs):
        try:
            item = Item.objects.get(uuid=kwargs['pk'])

        except:
            import traceback
            traceback.print_exc()
            return HttpResponseRedirect(reverse_lazy('items'))

        person_id = request.POST['person']
        person = Person.objects.get(pk=person_id)
        role_id = request.POST['role']
        role = PersonItemRelationRole.objects.get(pk=role_id)

        try:
            person_item_relation = PersonItemRelation.objects.get(item=item, person=person, role=role)
            messages.add_message(self.request, messages.WARNING,
                                 _("This person was already linked to this item as %s." % role))
        except ObjectDoesNotExist as e:
            person_item_relation = PersonItemRelation(item=item, person=person, role=role)
            person_item_relation.save()

        return HttpResponseRedirect(self.get_success_url())


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class PersonItemRelationRoleDeleteView(DeleteView):
    model = PersonItemRelationRole
    success_url = reverse_lazy('personitemrelationroles')


# Publication views
class PublicationTableView(ListView):
    model = Publication
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Publication.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PublicationTableView, self).get_context_data(**kwargs)
        filter = PublicationFilter(self.request.GET, queryset=self.get_queryset())

        table = PublicationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "publication"
        context['add_url'] = reverse_lazy('add_publication')

        return context


class PublicationDetailView(DetailView):
    model = Publication


class PublicationCreateView(CreateView):
    model = Publication
    template_name = 'generic_form.html'
    form_class = PublicationModelForm
    success_url = reverse_lazy('publications')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "publication"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class PublicationUpdateView(UpdateView):
    model = Publication
    template_name = 'generic_form.html'
    form_class = PublicationModelForm
    success_url = reverse_lazy('publications')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "publication"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class PublicationDeleteView(DeleteView):
    model = Publication
    success_url = reverse_lazy('publications')


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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


class WorkDetailView(DetailView):
    model = Work


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


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

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class WorkSubjectDeleteView(DeleteView):
    model = WorkSubject
    success_url = reverse_lazy('worksubjects')
