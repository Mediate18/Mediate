import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from .models import *


# Moderation table
class ModerationTable(tables.Table):
    edit = tables.LinkColumn('change_moderation', text='Edit', args=[A('pk')],
                         orderable=False, empty_values=())

    class Meta:
        model = Moderation
        attrs = {'class': 'table table-sortable'}