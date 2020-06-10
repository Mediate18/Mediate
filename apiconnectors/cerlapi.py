
from dal import autocomplete
from django.http import JsonResponse
import requests

cerl_search_url = 'https://data.cerl.org/thesaurus/_search'
cerl_record_url = 'http://thesaurus.cerl.org/record/'
cerl_record_url_api =   'https://data.cerl.org/thesaurus/'


def cerl_suggest(query, cerl_search_field="name"):
    response = requests.get(cerl_search_url,
                            params={'query': cerl_search_field+':'+query+'*'},
                            headers={'accept': 'application/json'})
    if response.status_code == requests.codes.ok:
        return response.json().get('rows', None) or []
    else:
        return []

def get_names(item, cerl_search_field):
    if cerl_search_field in item:
        return ", ".join([str(name) for name in item[cerl_search_field] if name])
    return ""

def get_record(id):
    response = requests.get(cerl_record_url_api+id, headers={'accept': 'application/json'})
    if response.status_code == requests.codes.ok:
        parts = response.json().get('data').get('heading')[0].get('part')
        names = [list(part.values())[0] for part in parts]
        return "{}, {}".format("".join(names[:1]), " ".join(names[1:]))
    else:
        return "- no data -"

class CerlSuggest(autocomplete.Select2ListView):
    cerl_search_field = "placeName"

    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'results': self.get_api_list()
        })

    def get_api_list(self):
        result = cerl_suggest(self.q, self.cerl_search_field)

        return [dict(
                id=item['id'],
                id_number=item['id'],
                text=item['name_display_line'] + " - <small>"
                     + get_names(item, self.cerl_search_field)
                     + "</small>",
                nametype='',
                external_url=cerl_record_url+item['id'],
                url_type='Cerl',
                clean_text=item['name_display_line']
            ) for item in result]


class CerlSuggestPublisher(CerlSuggest):
    cerl_search_field = "imprintName"
