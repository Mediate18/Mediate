
from dal import autocomplete
from django.http import JsonResponse
import requests

cerl_search_url = 'https://data.cerl.org/thesaurus/_search'
cerl_record_url = 'http://thesaurus.cerl.org/record/'


def cerl_suggest(query):
    response = requests.get(cerl_search_url,
                            params={'query': 'placeName:'+query+'*'},
                            headers={'accept': 'application/json'})
    if response.status_code == requests.codes.ok:
        return response.json().get('rows', None) or []
    else:
        return []


class CerlSuggest(autocomplete.Select2ListView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'results': self.get_api_list()
        })

    def get_api_list(self):
        result = cerl_suggest(self.q)

        return [dict(
                id=item['id'],
                id_number=item['id'],
                text=item['name_display_line'] + " - <small>"
                     + ", ".join([str(name) for name in item['placeName'] if name])
                     + "</small>",
                nametype='',
                external_url=cerl_record_url+item['id'],
                url_type='Cerl',
                clean_text=item['name_display_line']
            ) for item in result]
