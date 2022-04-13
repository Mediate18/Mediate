from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import *
from guardian.admin import GuardedModelAdmin


@admin.register(Collection)
class CollectionAdmin(SimpleHistoryAdmin):
    pass


@admin.register(CollectionType)
class CollectionTypeAdmin(SimpleHistoryAdmin):
    pass


@admin.register(PersonCollectionRelation)
class PersonCollectionRelationAdmin(SimpleHistoryAdmin):
    pass


@admin.register(PersonCollectionRelationRole)
class PersonCollectionRelationRoleAdmin(SimpleHistoryAdmin):
    pass


@admin.register(PersonCollection_TMPRelation)
class PersonCollection_TMPRelationAdmin(SimpleHistoryAdmin):
    pass


@admin.register(Collection_TMP)
class Collection_TMPAdmin(SimpleHistoryAdmin):
    search_fields = ['name']


@admin.register(Dataset)
class DatasetAdmin(GuardedModelAdmin, SimpleHistoryAdmin):
    pass
