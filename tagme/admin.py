from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from tagme.models import Tag, TaggedEntity


@admin.register(Tag)
class TagAdmin(SimpleHistoryAdmin):
    pass


@admin.register(TaggedEntity)
class TaggedEntityAdmin(SimpleHistoryAdmin):
    pass
