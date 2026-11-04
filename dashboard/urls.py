from django.urls import path

from dashboard.views import view_totals, collection_count, bookitems_count, work_count, person_count, \
    country_city_count, language_count, itempersonrelation_count, itemworkrelation_count, itemswithdate_count, \
    itemswithplaceofpublication_count, itemswithpublisher_count, personswithplaceofbirth_count, \
    personswithplaceofdeath_count, bookswithlanguage_count, bookswithparisiancategory_count

urlpatterns = [
    path(r'', view_totals, name='totals'),
    path(r'collection_count', collection_count, name='collection_count'),
    path(r'bookitems_count', bookitems_count, name='bookitems_count'),
    path(r'work_count', work_count, name='work_count'),
    path(r'person_count', person_count, name='person_count'),
    path(r'country_city_count', country_city_count, name='country_city_count'),
    path(r'language_count', language_count, name='language_count'),
    path(r'itempersonrelation_count', itempersonrelation_count, name='itempersonrelation_count'),
    path(r'itemworkrelation_count', itemworkrelation_count, name='itemworkrelation_count'),
    path(r'itemswithdate_count', itemswithdate_count, name='itemswithdate_count'),
    path(r'itemswithplaceofpublication_count', itemswithplaceofpublication_count, name='itemswithplaceofpublication_count'),
    path(r'itemswithpublisher_count', itemswithpublisher_count, name='itemswithpublisher_count'),
    path(r'personswithplaceofbirth_count', personswithplaceofbirth_count, name='personswithplaceofbirth_count'),
    path(r'personswithplaceofdeath_count', personswithplaceofdeath_count, name='personswithplaceofdeath_count'),
    path(r'bookswithlanguage_count', bookswithlanguage_count, name='bookswithlanguage_count'),
    path(r'bookswithparisiancategory_count', bookswithparisiancategory_count, name='bookswithparisiancategory_count'),
]