from django.contrib import admin
from items.models import *


class BindingMaterialDetailsAdmin(admin.ModelAdmin):
    pass


admin.site.register(BindingMaterialDetails, BindingMaterialDetailsAdmin)


class BindingMaterialDetailsEquivalentAdmin(admin.ModelAdmin):
    pass


admin.site.register(BindingMaterialDetailsEquivalent, BindingMaterialDetailsEquivalentAdmin)


class BookFormatAdmin(admin.ModelAdmin):
    pass


admin.site.register(BookFormat, BookFormatAdmin)


class BookFormatEquivalentAdmin(admin.ModelAdmin):
    pass


admin.site.register(BookFormatEquivalent, BookFormatEquivalentAdmin)


class ItemAdmin(admin.ModelAdmin):
    search_fields = ['title_work__text']


admin.site.register(Item, ItemAdmin)


class CatalogueSourceAdmin(admin.ModelAdmin):
    pass


admin.site.register(CatalogueSource, CatalogueSourceAdmin)


class CatalogueAdmin(admin.ModelAdmin):
    pass


admin.site.register(Catalogue, CatalogueAdmin)


class CatalogueEntryAdmin(admin.ModelAdmin):
    pass


admin.site.register(CatalogueEntry, CatalogueEntryAdmin)


class CatalogueTypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(CatalogueType, CatalogueTypeAdmin)


class CollectionAdmin(admin.ModelAdmin):
    pass


admin.site.register(Collection, CollectionAdmin)


class PersonCollectionRelationAdmin(admin.ModelAdmin):
    pass


admin.site.register(PersonCollectionRelation, PersonCollectionRelationAdmin)


class LanguageAdmin(admin.ModelAdmin):
    pass


admin.site.register(Language, LanguageAdmin)


class PersonAdmin(admin.ModelAdmin):
    pass


admin.site.register(Person, PersonAdmin)


class PersonItemRelationAdmin(admin.ModelAdmin):
    pass


admin.site.register(PersonItemRelation, PersonItemRelationAdmin)


class PersonItemRelationRoleAdmin(admin.ModelAdmin):
    pass


admin.site.register(PersonItemRelationRole, PersonItemRelationRoleAdmin)


class PersonCatalogueRelationAdmin(admin.ModelAdmin):
    pass


admin.site.register(PersonCatalogueRelation, PersonCatalogueRelationAdmin)


class PersonCatalogueRelationRoleAdmin(admin.ModelAdmin):
    pass


admin.site.register(PersonCatalogueRelationRole, PersonCatalogueRelationRoleAdmin)


class PlaceAdmin(admin.ModelAdmin):
    pass


admin.site.register(Place, PlaceAdmin)


class PlaceEquivalentAdmin(admin.ModelAdmin):
    pass


admin.site.register(PlaceEquivalent, PlaceEquivalentAdmin)


class PlaceTypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(PlaceType, PlaceTypeAdmin)


class PublisherAdmin(admin.ModelAdmin):
    pass


admin.site.register(Publisher, PublisherAdmin)


class PublisherEquivalentAdmin(admin.ModelAdmin):
    pass


admin.site.register(PublisherEquivalent, PublisherEquivalentAdmin)


class TitleWorkAdmin(admin.ModelAdmin):
    pass


admin.site.register(TitleWork, TitleWorkAdmin)
