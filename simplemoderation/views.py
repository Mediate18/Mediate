from django.contrib import messages
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db import transaction

# from django.contrib.contenttypes.models import ContentType

from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse_lazy
from django.shortcuts import redirect
import django_tables2

from datetime import datetime
from collections import OrderedDict

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
    template_name = 'simplemoderation/moderation_form.html'
    form_class = ModerationModelForm
    success_url = reverse_lazy('moderations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = _("update")
        context['object_name'] = "moderation"

        context['original_exists'], context['new_exists'], context['changes'] = self.get_changes()

        return context

    def get(self, request, *args, **kwargs):
        """
        Check whether the moderation to be edited is pending. Otherwise fail with a messages.
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        obj = self.get_object()
        if obj.state != ModerationState.PENDING.value:
            messages.add_message(self.request, messages.WARNING,
                                 _("This moderation is not pending."))
            return redirect(self.success_url)
        else:
            return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        moderation = form.save(commit=False)

        # If approved, save or delete the object
        try:
            with transaction.atomic():
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
                        message = _("ERROR: Something went wrong when handling moderation {}")\
                            .format(str(moderation.pk))
                        raise Exception(message)

                moderation.moderator = self.request.user
                moderation.moderated_datetime = timezone.now()
                moderation.save()
        except Exception as e:
            messages.add_message(self.request, messages.ERROR, str(e))

        return redirect(self.success_url)

    def get_changes(self):
        """
        Puts the changes between the original and new object in an ordered dict
        :return: OrderedDict: ordered dict containing the changes
        """
        moderation = self.get_object()

        # Determine whether there is an original and new object
        original_exists = True if moderation.action in (ModerationAction.UPDATE.value, ModerationAction.DELETE.value) \
            else False
        new_exists = True if moderation.action in (ModerationAction.UPDATE.value, ModerationAction.CREATE.value) \
            else False
        original = moderation.content_object if original_exists else None
        new = moderation.data if new_exists else None

        # Get all model fields except for the primary key
        if original_exists:
            fields = [f for f in original._meta.fields if not f.primary_key]
        else:
            fields = [f for f in new._meta.fields if
                      not f.primary_key]  # All model fields except for the primary key

        # Determine whether a field has changed (always true for creation and deletion)
        changes = OrderedDict()
        for field in fields:
            changes[field] = {}
            if original_exists:
                original_field = getattr(original, field.name)
                changes[field]['original'] = original_field
            if new_exists:
                new_field = getattr(new, field.name)
                changes[field]['new'] = new_field
            if original_exists and new_exists and original_field == new_field:
                changes[field]['changed'] = False
            else:
                changes[field]['changed'] = True
        return (original_exists, new_exists, changes)
