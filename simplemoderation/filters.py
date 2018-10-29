import django_filters
from django_select2.forms import Select2Widget, Select2MultipleWidget
from django.db.models import Q, Subquery
from django.contrib.auth.models import Permission
from .models import *


# Moderation filter
class ModerationFilter(django_filters.FilterSet):
    editor = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.filter(
            Q(groups__permissions=Permission.objects.get(codename='add_moderation')) |
            Q(user_permissions=Permission.objects.get(codename='add_moderation'))
        ).distinct(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
    )
    created_datetime = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(attrs={'placeholder': 'YYYY-MM-DD'})
    )
    action = django_filters.MultipleChoiceFilter(
        choices=[(tag.value, tag.name.capitalize()) for tag in ModerationAction],
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
    )
    content_type = django_filters.MultipleChoiceFilter(
        choices=[(ct.id, ct.model.capitalize()) for ct in registered_content_types],
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
    )
    master = django_filters.ModelChoiceFilter(
        queryset=Moderation.objects.filter(master=None,
                                           id__in=Subquery(Moderation.objects.exclude(master=None).values('master'))),
        widget=Select2Widget()
    )
    state = django_filters.MultipleChoiceFilter(
        choices=[(tag.value, tag.name.capitalize()) for tag in ModerationState],
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
    )
    moderator = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.filter(
            Q(groups__permissions=Permission.objects.get(codename='change_moderation')) |
            Q(user_permissions=Permission.objects.get(codename='change_moderation'))
        ).distinct(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': "Select multiple"},),
    )
    reason = django_filters.Filter(lookup_expr='icontains')

    class Meta:
        model = Moderation
        exclude = ('data', 'object_pk', 'moderated_datetime')
