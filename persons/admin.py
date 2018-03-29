from django.contrib import admin
from .models import *


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonPersonRelation)
class PersonPersonRelationAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonPersonRelationType)
class PersonPersonRelationTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonProfession)
class PersonProfessionAdmin(admin.ModelAdmin):
    pass


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    pass


@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    pass


@admin.register(Religion)
class ReligionAdmin(admin.ModelAdmin):
    pass


@admin.register(ReligiousAffiliation)
class ReligiousAffiliationAdmin(admin.ModelAdmin):
    pass


@admin.register(Residence)
class ResidenceAdmin(admin.ModelAdmin):
    pass
