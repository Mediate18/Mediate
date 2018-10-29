import django_tables2 as tables
from django.utils.html import format_html
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from .models import *


# Moderation table
class ModerationTable(tables.Table):
    id = tables.Column(orderable=False, verbose_name=_("Moderate"))

    class Meta:
        model = Moderation
        attrs = {'class': 'table table-sortable'}
        fields = ('editor', 'created_datetime', 'action', 'content_type', 'data', 'master', 'state', 'reason', 'id',)

    def render_action(self, record):
        return ModerationAction(record.action).name.capitalize()

    def render_content_type(self, value):
        return value.name.capitalize()

    def render_state(self, record):
        return ModerationState(record.state).name.capitalize()

    def render_id(self, record):
        moderation = record
        if moderation.state == ModerationState.PENDING.value and \
                (moderation.master is None or moderation.master.state != ModerationState.PENDING.value):
            return format_html('<a title="{}" href="{}"><span class="glyphicon glyphicon-pencil"></a>'
                               .format(_("Moderate"), reverse_lazy('change_moderation', args=[record.id])))
        else:
            return ""
