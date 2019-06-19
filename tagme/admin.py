from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from guardian.admin import GuardedModelAdmin
from tagme.models import Tag, TaggedEntity


@admin.register(Tag)
class TagAdmin(GuardedModelAdmin):
    pass


@admin.register(TaggedEntity)
class TaggedEntityAdmin(SimpleHistoryAdmin):
    pass
