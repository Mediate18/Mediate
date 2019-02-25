from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import *


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


@admin.register(PersonCollectionRelation)
class PersonCollectionRelationAdmin(SimpleHistoryAdmin):
    pass


@admin.register(Collection)
class CollectionAdmin(SimpleHistoryAdmin):
    pass