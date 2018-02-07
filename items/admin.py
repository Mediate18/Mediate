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


class BookItemAdmin(admin.ModelAdmin):
    search_fields = ['title_work__text']


admin.site.register(BookItem, BookItemAdmin)


class CatalogueAdmin(admin.ModelAdmin):
    pass


admin.site.register(Catalogue, CatalogueAdmin)


class CatalogueItemAdmin(admin.ModelAdmin):
    pass


admin.site.register(CatalogueItem, CatalogueItemAdmin)


class CatalogueTypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(CatalogueType, CatalogueTypeAdmin)


class LanguageAdmin(admin.ModelAdmin):
    pass


admin.site.register(Language, LanguageAdmin)


class PersonAdmin(admin.ModelAdmin):
    pass


admin.site.register(Person, PersonAdmin)


class PersonBookItemRelationAdmin(admin.ModelAdmin):
    pass


admin.site.register(PersonBookItemRelation, PersonBookItemRelationAdmin)


class PersonBookItemRelationTypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(PersonBookItemRelationType, PersonBookItemRelationTypeAdmin)


class PersonCatalogueRelationAdmin(admin.ModelAdmin):
    pass


admin.site.register(PersonCatalogueRelation, PersonCatalogueRelationAdmin)


class PersonCatalogueRelationTypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(PersonCatalogueRelationType, PersonCatalogueRelationTypeAdmin)


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
