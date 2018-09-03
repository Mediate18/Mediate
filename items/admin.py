from django.contrib import admin
from .models import *

# TODO The next bit should be in a more global place, but I could not find one (Micha, 2018-04-06)
from django.contrib.auth.models import Permission
admin.site.register(Permission)


@admin.register(BookFormat)
class BookFormatAdmin(admin.ModelAdmin):
    pass


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    search_fields = ['work__title']


@admin.register(ItemAuthor)
class ItemAuthorAdmin(admin.ModelAdmin):
    pass


@admin.register(ItemItemTypeRelation)
class ItemItemTypeRelationAdmin(admin.ModelAdmin):
    pass


@admin.register(ItemLanguageRelation)
class ItemLanguageRelationAdmin(admin.ModelAdmin):
    pass


@admin.register(ItemMaterialDetailsRelation)
class ItemMaterialDetailsRelationAdmin(admin.ModelAdmin):
    pass


@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(ItemWorkRelation)
class ItemWorkRelationAdmin(admin.ModelAdmin):
    pass


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    pass


@admin.register(MaterialDetails)
class MaterialDetailsAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonItemRelation)
class PersonItemRelationAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonItemRelationRole)
class PersonItemRelationRoleAdmin(admin.ModelAdmin):
    pass


@admin.register(Manifestation)
class ManifestationAdmin(admin.ModelAdmin):
    pass


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    pass


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    pass


@admin.register(WorkAuthor)
class WorkAuthorAdmin(admin.ModelAdmin):
    pass


@admin.register(WorkSubject)
class WorkSubjectAdmin(admin.ModelAdmin):
    pass


