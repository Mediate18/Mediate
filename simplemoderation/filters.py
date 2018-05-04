import django_filters
from .models import *


# Moderation filter
class ModerationFilter(django_filters.FilterSet):
    class Meta:
        model = Moderation
        fields = "__all__"