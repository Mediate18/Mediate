from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import *
from guardian.admin import GuardedModelAdmin


@admin.register(Catalogue)
class CatalogueAdmin(SimpleHistoryAdmin):
    pass


@admin.register(CatalogueType)
class CatalogueTypeAdmin(SimpleHistoryAdmin):
    pass


@admin.register(PersonCatalogueRelation)
class PersonCatalogueRelationAdmin(SimpleHistoryAdmin):
    pass


@admin.register(PersonCatalogueRelationRole)
class PersonCatalogueRelationRoleAdmin(SimpleHistoryAdmin):
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
