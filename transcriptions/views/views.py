from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.forms import inlineformset_factory

from django.contrib.contenttypes.models import ContentType

from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy
import django_tables2

from simplemoderation.models import Moderation

from ..forms import *
from ..filters import *
from ..tables import *


# DocumentScan views
class DocumentScanTableView(ListView):
    model = DocumentScan
    template_name = 'generic_list.html'

    def get_queryset(self):
        return DocumentScan.objects.all()

    def get_context_data(self, **kwargs):
        context = super(DocumentScanTableView, self).get_context_data(**kwargs)
        filter = DocumentScanFilter(self.request.GET, queryset=self.get_queryset())

        table = DocumentScanTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "documentscan"
        context['add_url'] = reverse_lazy('add_documentscan')

        return context


class DocumentScanDetailView(DetailView):
    model = DocumentScan


class DocumentScanCreateView(CreateView):
    model = DocumentScan
    template_name = 'generic_form.html'
    form_class = DocumentScanModelForm
    success_url = reverse_lazy('documentscans')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "documentscan"
        return context


class DocumentScanUpdateView(UpdateView):
    model = DocumentScan
    template_name = 'generic_form.html'
    form_class = DocumentScanModelForm
    success_url = reverse_lazy('documentscans')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "documentscan"
        return context


class DocumentScanDeleteView(DeleteView):
    model = DocumentScan
    success_url = reverse_lazy('documentscans')


# SourceMaterial views
class SourceMaterialTableView(ListView):
    model = SourceMaterial
    template_name = 'generic_list.html'

    def get_queryset(self):
        return SourceMaterial.objects.all()

    def get_context_data(self, **kwargs):
        context = super(SourceMaterialTableView, self).get_context_data(**kwargs)
        filter = SourceMaterialFilter(self.request.GET, queryset=self.get_queryset())

        table = SourceMaterialTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name'] = "sourcematerial"
        context['add_url'] = reverse_lazy('add_sourcematerial')

        return context


class SourceMaterialDetailView(DetailView):
    model = SourceMaterial


class SourceMaterialCreateView(CreateView):
    model = SourceMaterial
    template_name = 'generic_form.html'
    form_class = SourceMaterialModelForm
    success_url = reverse_lazy('sourcematerials')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = "sourcematerial"
        return context


class SourceMaterialUpdateView(UpdateView):
    model = SourceMaterial
    template_name = 'generic_form.html'
    form_class = SourceMaterialModelForm
    success_url = reverse_lazy('sourcematerials')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "sourcematerial"
        return context


class SourceMaterialDeleteView(DeleteView):
    model = SourceMaterial
    success_url = reverse_lazy('sourcematerials')


# Transcription views
class TranscriptionTableView(ListView):
    model = Transcription
    template_name = 'generic_list.html'

    def get_queryset(self):
        return Transcription.objects.all()

    def get_context_data(self, **kwargs):
        context = super(TranscriptionTableView, self).get_context_data(**kwargs)
        filter = TranscriptionFilter(self.request.GET, queryset=self.get_queryset())

        table = TranscriptionTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name_plural'] = Transcription._meta.verbose_name_plural
        context['add_url'] = reverse_lazy('add_transcription')

        return context


class TranscriptionDetailView(DetailView):
    model = Transcription
    template_name = 'transcription_detail.html'


DocumentScanFormset = inlineformset_factory(Transcription, DocumentScan, fields=('scan',), extra=2)


class TranscriptionCreateView(CreateView):
    model = Transcription
    template_name = 'transcription_form.html'
    form_class = TranscriptionModelForm
    success_url = reverse_lazy('transcriptions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = Transcription._meta.verbose_name
        if self.request.POST:
            context['documentscans'] = DocumentScanFormset(self.request.POST, self.request.FILES)
        else:
            context['documentscans'] = DocumentScanFormset()

        # Remove the option to delete for new objects
        for form in context['documentscans']:
            if not form.initial:
                del form.fields['DELETE']
                
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['documentscans']
        if formset.is_valid():
            transcription = form.save(commit=False)
            transcription.author = self.request.user

            # if not self.request.user.is_superuser:
            #     messages.add_message(self.request, messages.SUCCESS,
            #                          _("Your changes will be sent to a moderator for reviewing."))
            #     moderation = Moderation.create(editor=self.request.user, obj=transcription)
            #     moderation.save()
            # else:
            transcription.save()
            formset.instance = transcription
            formset.save()
        else:
            return self.render_to_response(self.get_context_data(form=form))

        return redirect(self.success_url)


class TranscriptionUpdateView(UpdateView):
    model = Transcription
    template_name = 'transcription_form.html'
    form_class = TranscriptionModelForm
    success_url = reverse_lazy('transcriptions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = Transcription._meta.verbose_name
        if self.request.POST:
            context['documentscans'] = DocumentScanFormset(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['documentscans'] = DocumentScanFormset(instance=self.object)

        # Remove the option to delete for new objects
        for form in context['documentscans']:
            if not form.initial:
                del form.fields['DELETE']

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['documentscans']
        if formset.is_valid():
            transcription = form.save(commit=False)
            transcription.author = self.request.user

            # if not self.request.user.is_superuser:
            #     messages.add_message(self.request, messages.SUCCESS,
            #                          _("Your changes will be sent to a moderator for reviewing."))
            #     moderation = Moderation.update(editor=self.request.user, obj=transcription)
            #     moderation.save()
            # else:
            transcription.save()
            formset.instance = transcription
            formset.save()

        return redirect(self.success_url)


class TranscriptionDeleteView(DeleteView):
    model = Transcription
    success_url = reverse_lazy('transcriptions')


# ShelfMark views
class ShelfMarkTableView(ListView):
    model = ShelfMark
    template_name = 'generic_list.html'

    def get_context_data(self, **kwargs):
        context = super(ShelfMarkTableView, self).get_context_data(**kwargs)
        filter = ShelfMarkFilter(self.request.GET, queryset=self.get_queryset())

        table = ShelfMarkTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['action'] = _("add")
        context['object_name_plural'] = ShelfMark._meta.verbose_name_plural
        context['add_url'] = reverse_lazy('add_shelfmark')

        return context


class ShelfMarkDetailView(DetailView):
    model = ShelfMark
    template_name = 'generic_detail.html'


ShelfMarkFormset = inlineformset_factory(ShelfMark, DocumentScan, fields=('scan',), extra=2)


class ShelfMarkCreateView(CreateView):
    model = ShelfMark
    template_name = 'shelfmark_form.html'
    form_class = ShelfMarkModelForm
    success_url = reverse_lazy('shelfmarks')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("add")
        context['object_name'] = ShelfMark._meta.verbose_name
        if self.request.POST:
            context['documentscans'] = ShelfMarkFormset(self.request.POST, self.request.FILES)
        else:
            context['documentscans'] = ShelfMarkFormset()

        # Remove the option to delete for new objects
        for form in context['documentscans']:
            if not form.initial:
                del form.fields['DELETE']

        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['documentscans']
        if formset.is_valid():
            # Save shelf-mark
            shelfmark = form.save()

            # Save document scans
            formset.instance = shelfmark
            formset.save()

            # Connect shelf-mark to collection(s)
            for collection in form.cleaned_data['collection']:
                collection.shelf_mark = shelfmark
                collection.save()
        else:
            return self.render_to_response(self.get_context_data(form=form))

        return redirect(self.success_url)


class ShelfMarkUpdateView(UpdateView):
    model = ShelfMark
    template_name = 'shelfmark_form.html'
    form_class = ShelfMarkModelForm
    success_url = reverse_lazy('shelfmarks')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = ShelfMark._meta.verbose_name
        if self.request.POST:
            context['documentscans'] = ShelfMarkFormset(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['documentscans'] = ShelfMarkFormset(instance=self.object)

        # Remove the option to delete for new objects
        for form in context['documentscans']:
            if not form.initial:
                del form.fields['DELETE']

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['documentscans']
        if formset.is_valid():
            # Save shelf-mark
            shelfmark = form.save()

            # Save document scans
            formset.instance = shelfmark
            formset.save()

            # Connect shelf-mark to collection(s)
            for collection in form.cleaned_data['collection']:
                collection.shelf_mark = shelfmark
                collection.save()
        else:
            return self.render_to_response(self.get_context_data(form=form))

        return redirect(self.success_url)


class ShelfMarkDeleteView(DeleteView):
    model = ShelfMark
    success_url = reverse_lazy('shelfmarks')
