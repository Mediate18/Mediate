from django.contrib import messages
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.db import transaction
from django.db.models import Count

from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from django.urls import reverse
import django_tables2

from django.http import JsonResponse
import re
import json
import requests

from apiconnectors.cerlapi import CerlSuggest, cerl_record_url

from simplemoderation.tools import moderate, ModeratedCreateView
from mediate.views import GenericDetailView

from ..forms import *
from ..filters import *
from ..tables import *


# Person views
class PersonTableView(ListView):
    model = Person
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Person.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PersonTableView, self).get_context_data(**kwargs)
        filter = PersonFilter(self.request.GET, queryset=self.get_queryset())

        table = PersonTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "person"
        context['add_url'] = reverse_lazy('add_person')

        return context


class PersonRankingTableView(ListView):
    model = Person
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Person.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PersonRankingTableView, self).get_context_data(**kwargs)
        filter = PersonRankingFilter(self.request.GET, queryset=self.get_queryset())

        table = PersonRankingTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name_plural'] = "person ranking"
        context['add_url'] = reverse_lazy('add_person')

        return context


class PersonDetailView(DetailView):
    model = Person


class PersonCreateView(CreateView):
    model = Person
    template_name = 'persons/person_form.html'
    form_class = PersonModelForm
    success_url = reverse_lazy('persons')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "person"
        context['js_variables'] = json.dumps({'viaf_select_id': PersonModelForm.suggest_select_ids})
        if self.request.POST:
            context['alternativepersonnames'] = AlternativePersonNameFormSet(self.request.POST,
                                                                                   instance=self.object)
        else:
            context['alternativepersonnames'] = AlternativePersonNameFormSet(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        # Hacking the POST dict to enable users to enter a Cerl ID as Place identifier
        # TODO Find a more elegant method
        post_parameters = request.POST.copy()
        for city_field in ['city_of_birth', 'city_of_death']:
            if city_field in post_parameters:
                city = post_parameters.pop(city_field, None)
                if city[0].startswith('cnl'):
                    response = requests.get(cerl_record_url + city[0], headers={'accept': 'application/json'})
                    place_name = response.json().get('data')['heading'][0]['part'][0]['entry']
                    (city_obj, created) = Place.objects.get_or_create(name=place_name, cerl_id=city[0])
                    print(city_obj)
                    post_parameters[city_field] = str(city_obj.uuid)
                else:
                    post_parameters[city_field] = city[0]

        form = PersonModelForm(data=post_parameters)
        self.object = form.instance
        if form.is_valid():
            context = self.get_context_data()
            alternativepersonnames = context['alternativepersonnames']
            with transaction.atomic():
                self.object = form.save()
                if alternativepersonnames and alternativepersonnames.is_valid():
                    alternativepersonnames.instance = self.object
                    alternativepersonnames.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
                'short_name': self.object.short_name,
            }
            return JsonResponse(data)
        else:
            return response


class PersonCreateViewSimple(PersonCreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alternativepersonnames'] = None
        return context

@moderate()
class PersonUpdateView(UpdateView):
    model = Person
    template_name = 'persons/person_form.html'
    form_class = PersonModelForm
    success_url = reverse_lazy('persons')

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "person"
        context['js_variables'] = json.dumps({'viaf_select_id': PersonModelForm.suggest_select_ids})
        if self.request.POST:
            context['alternativepersonnames'] = AlternativePersonNameFormSet(self.request.POST,
                                                                                   instance=self.object)
        else:
            context['alternativepersonnames'] = AlternativePersonNameFormSet(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        # Hacking the POST dict to enable users to enter a Cerl ID as Place identifier
        # TODO Find a more elegant method
        post_parameters = request.POST.copy()
        for city_field in ['city_of_birth', 'city_of_death']:
            if city_field in post_parameters:
                city = post_parameters.pop(city_field, None)
                if city[0].startswith('cnl'):
                    (city_obj, created) = Place.objects.get_or_create(cerl_id=city[0])
                    post_parameters[city_field] = str(city_obj.uuid)
                else:
                    post_parameters[city_field] = city[0]

        form = PersonModelForm(instance=self.get_object(), data=post_parameters)
        if form.is_valid():
            context = self.get_context_data()
            alternativepersonnames = context['alternativepersonnames']
            with transaction.atomic():
                print("Form city_of_birth", form.cleaned_data['city_of_birth'])
                self.object = form.save()
                if alternativepersonnames.is_valid():
                    alternativepersonnames.instance = self.object
                    alternativepersonnames.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class PersonDeleteView(DeleteView):
    model = Person
    success_url = reverse_lazy('persons')


# PersonPersonRelation views
class PersonPersonRelationTableView(ListView):
    model = PersonPersonRelation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return PersonPersonRelation.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PersonPersonRelationTableView, self).get_context_data(**kwargs)
        filter = PersonPersonRelationFilter(self.request.GET, queryset=self.get_queryset())

        table = PersonPersonRelationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "personpersonrelation"
        context['add_url'] = reverse_lazy('add_personpersonrelation')

        return context


class PersonPersonRelationDetailView(DetailView):
    model = PersonPersonRelation


class PersonPersonRelationCreateView(CreateView):
    model = PersonPersonRelation
    template_name = 'generic_form.html'
    form_class = PersonPersonRelationModelForm
    success_url = reverse_lazy('personpersonrelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "personpersonrelation"
        return context


class PersonPersonRelationUpdateView(UpdateView):
    model = PersonPersonRelation
    template_name = 'generic_form.html'
    form_class = PersonPersonRelationModelForm
    success_url = reverse_lazy('personpersonrelations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "personpersonrelation"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class PersonPersonRelationDeleteView(DeleteView):
    model = PersonPersonRelation
    success_url = reverse_lazy('personpersonrelations')


# PersonPersonRelationType views
class PersonPersonRelationTypeTableView(ListView):
    model = PersonPersonRelationType
    template_name = 'generic_list.html'

    def get_queryset(self):
        return PersonPersonRelationType.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PersonPersonRelationTypeTableView, self).get_context_data(**kwargs)
        filter = PersonPersonRelationTypeFilter(self.request.GET, queryset=self.get_queryset())

        table = PersonPersonRelationTypeTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "personpersonrelationtype"
        context['add_url'] = reverse_lazy('add_personpersonrelationtype')

        return context


class PersonPersonRelationTypeDetailView(DetailView):
    model = PersonPersonRelationType


class PersonPersonRelationTypeCreateView(CreateView):
    model = PersonPersonRelationType
    template_name = 'generic_form.html'
    form_class = PersonPersonRelationTypeModelForm
    success_url = reverse_lazy('personpersonrelationtypes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "personpersonrelationtype"
        return context


class PersonPersonRelationTypeUpdateView(UpdateView):
    model = PersonPersonRelationType
    template_name = 'generic_form.html'
    form_class = PersonPersonRelationTypeModelForm
    success_url = reverse_lazy('personpersonrelationtypes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "personpersonrelationtype"
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.SUCCESS,
                                 _("Your changes will be sent to a moderator for reviewing."))
        return super().form_valid(form)


class PersonPersonRelationTypeDeleteView(DeleteView):
    model = PersonPersonRelationType
    success_url = reverse_lazy('personpersonrelationtypes')


# PersonProfession views
class PersonProfessionTableView(ListView):
    model = PersonProfession
    template_name = 'generic_list.html'

    def get_queryset(self):
        return PersonProfession.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PersonProfessionTableView, self).get_context_data(**kwargs)
        filter = PersonProfessionFilter(self.request.GET, queryset=self.get_queryset())

        table = PersonProfessionTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "personprofession"
        context['add_url'] = reverse_lazy('add_personprofession')

        return context


class PersonProfessionDetailView(DetailView):
    model = PersonProfession


class PersonProfessionCreateView(CreateView):
    model = PersonProfession
    template_name = 'generic_form.html'
    form_class = PersonProfessionModelForm
    success_url = reverse_lazy('personprofessions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "personprofession"
        return context


class PersonProfessionUpdateView(UpdateView):
    model = PersonProfession
    template_name = 'generic_form.html'
    form_class = PersonProfessionModelForm
    success_url = reverse_lazy('personprofessions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "personprofession"
        return context


class PersonProfessionDeleteView(DeleteView):
    model = PersonProfession
    success_url = reverse_lazy('personprofessions')


# Country views
class CountryTableView(ListView):
    model = Country
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Country.objects.all()

    def get_context_data(self, **kwargs):
        context = super(CountryTableView, self).get_context_data(**kwargs)
        filter = CountryFilter(self.request.GET, queryset=self.get_queryset())

        table = CountryTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name_plural'] = self.model._meta.verbose_name_plural
        context['add_url'] = reverse_lazy('add_country')

        return context


class CountryDetailView(GenericDetailView):
    model = Country
    object_fields = ['name']


class CountryCreateView(CreateView):
    model = Country
    template_name = 'generic_form.html'
    form_class = CountryModelForm
    success_url = reverse_lazy('countries')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "country"
        return context


class CountryUpdateView(UpdateView):
    model = Country
    template_name = 'generic_form.html'
    form_class = CountryModelForm
    success_url = reverse_lazy('countries')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "country"
        return context


class CountryDeleteView(DeleteView):
    model = Country
    success_url = reverse_lazy('countries')


# Place views
class PlaceTableView(ListView):
    model = Place
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Place.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PlaceTableView, self).get_context_data(**kwargs)
        filter = PlaceFilter(self.request.GET, queryset=self.get_queryset())

        table = PlaceTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "place"
        context['add_url'] = reverse_lazy('add_place')

        return context


class PlaceLinksTableView(ListView):
    model = Place
    template_name = 'generic_list.html'

    def get_context_data(self, **kwargs):
        context = super(PlaceLinksTableView, self).get_context_data(**kwargs)
        filter = PlaceLinksFilter(self.request.GET, queryset=self.get_queryset())

        table = PlaceLinksTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name_plural'] = "Entities linked to places"
        context['add_url'] = reverse_lazy('add_place')

        return context


class PlaceDetailView(GenericDetailView):
    model = Place
    object_fields = ['name', 'cerl_id', 'country']


class PlaceCreateView(CreateView):
    model = Place
    template_name = 'generic_form.html'
    form_class = PlaceModelForm
    success_url = reverse_lazy('places')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "place"
        return context


class PlaceUpdateView(UpdateView):
    model = Place
    template_name = 'generic_form.html'
    form_class = PlaceModelForm
    success_url = reverse_lazy('places')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "place"
        return context


class PlaceDeleteView(DeleteView):
    model = Place
    success_url = reverse_lazy('places')


# Profession views
class ProfessionTableView(ListView):
    model = Profession
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Profession.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ProfessionTableView, self).get_context_data(**kwargs)
        filter = ProfessionFilter(self.request.GET, queryset=self.get_queryset())

        table = ProfessionTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "profession"
        context['add_url'] = reverse_lazy('add_profession')

        return context


class ProfessionDetailView(DetailView):
    model = Profession


class ProfessionCreateView(CreateView):
    model = Profession
    template_name = 'generic_form.html'
    form_class = ProfessionModelForm
    success_url = reverse_lazy('professions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "profession"
        return context


class ProfessionUpdateView(UpdateView):
    model = Profession
    template_name = 'generic_form.html'
    form_class = ProfessionModelForm
    success_url = reverse_lazy('professions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "profession"
        return context


class ProfessionDeleteView(DeleteView):
    model = Profession
    success_url = reverse_lazy('professions')


# Religion views
class ReligionTableView(ListView):
    model = Religion
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Religion.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ReligionTableView, self).get_context_data(**kwargs)
        filter = ReligionFilter(self.request.GET, queryset=self.get_queryset())

        table = ReligionTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "religion"
        context['add_url'] = reverse_lazy('add_religion')

        return context


class ReligionDetailView(DetailView):
    model = Religion


class ReligionCreateView(CreateView):
    model = Religion
    template_name = 'generic_form.html'
    form_class = ReligionModelForm
    success_url = reverse_lazy('religions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "religion"
        return context


class ReligionUpdateView(UpdateView):
    model = Religion
    template_name = 'generic_form.html'
    form_class = ReligionModelForm
    success_url = reverse_lazy('religions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "religion"
        return context


class ReligionDeleteView(DeleteView):
    model = Religion
    success_url = reverse_lazy('religions')


# ReligiousAffiliation views
class ReligiousAffiliationTableView(ListView):
    model = ReligiousAffiliation
    template_name = 'generic_list.html'

    def get_queryset(self):
        return ReligiousAffiliation.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ReligiousAffiliationTableView, self).get_context_data(**kwargs)
        filter = ReligiousAffiliationFilter(self.request.GET, queryset=self.get_queryset())

        table = ReligiousAffiliationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "religiousaffiliation"
        context['add_url'] = reverse_lazy('add_religiousaffiliation')

        return context


class ReligiousAffiliationDetailView(DetailView):
    model = ReligiousAffiliation


class ReligiousAffiliationCreateView(CreateView):
    model = ReligiousAffiliation
    template_name = 'generic_form.html'
    form_class = ReligiousAffiliationModelForm
    success_url = reverse_lazy('religiousaffiliations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "religiousaffiliation"
        return context


class ReligiousAffiliationUpdateView(UpdateView):
    model = ReligiousAffiliation
    template_name = 'generic_form.html'
    form_class = ReligiousAffiliationModelForm
    success_url = reverse_lazy('religiousaffiliations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "religiousaffiliation"
        return context


class ReligiousAffiliationDeleteView(DeleteView):
    model = ReligiousAffiliation
    success_url = reverse_lazy('religiousaffiliations')


# Residence views
class ResidenceTableView(ListView):
    model = Residence
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Residence.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ResidenceTableView, self).get_context_data(**kwargs)
        filter = ResidenceFilter(self.request.GET, queryset=self.get_queryset())

        table = ResidenceTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "residence"
        context['add_url'] = reverse_lazy('add_residence')

        return context


class ResidenceDetailView(DetailView):
    model = Residence


class ResidenceCreateView(CreateView):
    model = Residence
    template_name = 'generic_form.html'
    form_class = ResidenceModelForm
    success_url = reverse_lazy('residences')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "residence"
        return context


class ResidenceUpdateView(UpdateView):
    model = Residence
    template_name = 'generic_form.html'
    form_class = ResidenceModelForm
    success_url = reverse_lazy('residences')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "residence"
        return context


class ResidenceDeleteView(DeleteView):
    model = Residence
    success_url = reverse_lazy('residences')


class PlaceAndCerlSuggest(CerlSuggest):
    def get(self, request, *args, **kwargs):
        cerl_result = super().get_api_list()

        place_result_raw = Place.objects.filter(name__icontains=self.q)
        place_cerl_ids = set()
        place_result = []
        for obj in place_result_raw:
            id_number = re.match(r'.*?(\d+)$', obj.cerl_id).group(1) if obj.cerl_id else obj.uuid
            obj_dict = dict(
                id=obj.cerl_id if obj.cerl_id else obj.uuid,
                id_number=id_number,
                text='<i>' + escape(obj.name) + '</i>',
                nametype='',
                class_name="local_place",
                clean_text=escape(obj.name)
            )
            if obj.cerl_id:
                obj_dict['external_url'] = cerl_record_url + obj.cerl_id
                obj_dict['url_type'] = 'Cerl'
            else:
                obj_dict['external_url'] = request.build_absolute_uri(reverse('change_place', args=[obj.uuid]))
                obj_dict['url_type'] = 'internal'
            place_result.append(obj_dict)
            place_cerl_ids.add(id_number)

        return JsonResponse({
            'results': place_result + cerl_result
        })