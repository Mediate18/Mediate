from django.urls import path

from wikidata.views import WikidataSuggestView, ObjectExistsWikidataView


urlpatterns = [
     path('wikidata/', WikidataSuggestView.as_view(), name='wikidata'),
     path('object_exists_wikidata/<model_name>/<wikidata_id>/', ObjectExistsWikidataView.as_view(),
          name='object_exists_wikidata'),
]