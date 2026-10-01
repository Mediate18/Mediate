from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from wikidata.admin import WikidataAdminMixin
from .models import *


@admin.register(Person)
class PersonAdmin(WikidataAdminMixin, SimpleHistoryAdmin):
    fill_field_name = 'person_wikidata'
    autocomplete_fields = ["city_of_birth", "city_of_death",]


@admin.register(PersonPersonRelation)
class PersonPersonRelationAdmin(SimpleHistoryAdmin):
    pass


@admin.register(PersonPersonRelationType)
class PersonPersonRelationTypeAdmin(SimpleHistoryAdmin):
    pass


@admin.register(PersonProfession)
class PersonProfessionAdmin(SimpleHistoryAdmin):
    pass


@admin.register(Country)
class CountryAdmin(WikidataAdminMixin, SimpleHistoryAdmin):
    search_fields = ['name']
    fill_field_name = 'country_wikidata'


@admin.register(Place)
class PlaceAdmin(WikidataAdminMixin, SimpleHistoryAdmin):
    list_display = ('name', 'cerl_id', 'country', 'latitude', 'longitude')
    search_fields = ['name']
    fill_field_name = 'place_wikidata'
    autocomplete_fields = ["country",]


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


@admin.register(AlternativePersonName)
class AlternativePersonNameAdmin(SimpleHistoryAdmin):
    pass
