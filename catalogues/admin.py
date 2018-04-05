from django.contrib import admin
from .models import *


@admin.register(Catalogue)
class CatalogueAdmin(admin.ModelAdmin):
    pass


@admin.register(CatalogueType)
class CatalogueTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonCatalogueRelation)
class PersonCatalogueRelationAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonCatalogueRelationRole)
class PersonCatalogueRelationRoleAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonCollectionRelation)
class PersonCollectionRelationAdmin(admin.ModelAdmin):
    pass


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    pass