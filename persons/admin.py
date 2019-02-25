from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import *


@admin.register(Person)
class PersonAdmin(SimpleHistoryAdmin):
    pass


@admin.register(PersonPersonRelation)
class PersonPersonRelationAdmin(SimpleHistoryAdmin):
    pass


@admin.register(PersonPersonRelationType)
class PersonPersonRelationTypeAdmin(SimpleHistoryAdmin):
    pass


@admin.register(PersonProfession)
class PersonProfessionAdmin(SimpleHistoryAdmin):
    pass


@admin.register(Place)
class PlaceAdmin(SimpleHistoryAdmin):
    pass


@admin.register(Profession)
class ProfessionAdmin(SimpleHistoryAdmin):
    pass


@admin.register(Religion)
class ReligionAdmin(SimpleHistoryAdmin):
    pass


@admin.register(ReligiousAffiliation)
class ReligiousAffiliationAdmin(SimpleHistoryAdmin):
    pass


@admin.register(Residence)
class ResidenceAdmin(SimpleHistoryAdmin):
    pass
