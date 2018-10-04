import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from .models import *


# Moderation table
class ModerationTable(tables.Table):
    id = tables.LinkColumn('change_moderation', text='Moderate', args=[A('pk')], orderable=False, verbose_name="Moderate",
                           empty_values=[moderation.id for moderation in
                                         Moderation.objects.filter(state__in=[ModerationState.APPROVED.value,
                                                                              ModerationState.REJECTED.value])])

    class Meta:
        model = Moderation
        attrs = {'class': 'table table-sortable'}
        fields = ('editor', 'created_datetime', 'action', 'content_type', 'data', 'state', 'id',)

    def render_action(self, record):
        return ModerationAction(record.action).name.capitalize()

    def render_content_type(self, value):
        return value.name.capitalize()

    def render_state(self, record):
        return ModerationState(record.state).name.capitalize()

