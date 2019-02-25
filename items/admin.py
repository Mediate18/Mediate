from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import *

# TODO The next bit should be in a more global place, but I could not find one (Micha, 2018-04-06)
from django.contrib.auth.models import Permission
admin.site.register(Permission)


@admin.register(BookFormat)
class BookFormatAdmin(SimpleHistoryAdmin):
    pass


@admin.register(Item)
class ItemAdmin(SimpleHistoryAdmin):
    search_fields = ['work__title']


@admin.register(ItemAuthor)
class ItemAuthorAdmin(SimpleHistoryAdmin):
    pass


@admin.register(ItemItemTypeRelation)
class ItemItemTypeRelationAdmin(SimpleHistoryAdmin):
    pass


@admin.register(ItemLanguageRelation)
class ItemLanguageRelationAdmin(SimpleHistoryAdmin):
    pass


@admin.register(ItemMaterialDetailsRelation)
class ItemMaterialDetailsRelationAdmin(SimpleHistoryAdmin):
    pass


@admin.register(ItemType)
class ItemTypeAdmin(SimpleHistoryAdmin):
    pass


@admin.register(ItemWorkRelation)
class ItemWorkRelationAdmin(SimpleHistoryAdmin):
    pass


@admin.register(Language)
class LanguageAdmin(SimpleHistoryAdmin):
    pass


@admin.register(MaterialDetails)
class MaterialDetailsAdmin(SimpleHistoryAdmin):
    pass


@admin.register(PersonItemRelation)
class PersonItemRelationAdmin(SimpleHistoryAdmin):
    pass


@admin.register(PersonItemRelationRole)
class PersonItemRelationRoleAdmin(SimpleHistoryAdmin):
    pass


@admin.register(Manifestation)
class ManifestationAdmin(SimpleHistoryAdmin):
    pass


@admin.register(Publisher)
class PublisherAdmin(SimpleHistoryAdmin):
    pass


@admin.register(Subject)
class SubjectAdmin(SimpleHistoryAdmin):
    pass


@admin.register(Work)
class WorkAdmin(SimpleHistoryAdmin):
    pass


@admin.register(WorkAuthor)
class WorkAuthorAdmin(SimpleHistoryAdmin):
    pass


@admin.register(WorkSubject)
class WorkSubjectAdmin(SimpleHistoryAdmin):
    pass


