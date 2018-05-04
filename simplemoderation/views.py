from django.contrib import messages
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView

# from django.contrib.contenttypes.models import ContentType

from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy
import django_tables2

from datetime import datetime

from .forms import *
from .filters import *
from .tables import *


# Moderation views
class ModerationTableView(ListView):
    model = Moderation
    template_name = 'moderation_list.html'

    def get_queryset(self):
        return Moderation.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ModerationTableView, self).get_context_data(**kwargs)
        filter = ModerationFilter(self.request.GET, queryset=self.get_queryset())

        table = ModerationTable(filter.qs)
        django_tables2.RequestConfig(self.request, ).configure(table)

        context['filter'] = filter
        context['table'] = table

        context['object_name'] = "moderation"

        return context
    

class ModerationUpdateView(UpdateView):
    model = Moderation
    template_name = 'generic_form.html'
    form_class = ModerationModelForm
    success_url = reverse_lazy('moderations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "moderation"
        return context

    def form_valid(self, form):
        moderation = form.save(commit=False)

        # If approved, save or delete the object
        if moderation.state is ModerationState.APPROVED.value:
            if moderation.object_pk and moderation.action == ModerationAction.UPDATE.value:
                obj = moderation.data
                obj.pk = moderation.object_pk
                obj.save()
            elif not moderation.object_pk and moderation.action == ModerationAction.CREATE.value:
                obj = moderation.data
                obj.save()
            elif moderation.object_pk and moderation.action == ModerationAction.DELETE.value:
                obj = moderation.data
                obj.delete()
            else:
                # TODO
                message = "ERROR: Something went wrong when handling moderation %s" % str(moderation.pk)
                print(message)
                messages.add_message(self.request, messages.ERROR, _(message))

        moderation.moderator = self.request.user
        moderation.moderated_datetime = datetime.now()
        moderation.save()

        from django.shortcuts import redirect
        return redirect(self.success_url)