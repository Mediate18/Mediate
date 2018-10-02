from django.contrib import admin
from .models import *


@admin.register(Moderation)
class ModerationAdmin(admin.ModelAdmin):
    readonly_fields = ('editor', 'created_datetime', 'action', 'content_type', 'data',)