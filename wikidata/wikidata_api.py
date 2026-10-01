import requests
import logging
from django.conf import settings


logger = logging.getLogger(__name__)


WIKIDATA_API_HEADERS = {'accept': 'application/json',
                        'Authorization': f'Bearer {settings.WIKIDATA_API_KEY}',
                        'User-Agent': 'https://shewrote.rich.ru.nl/'}


def get_wikidata_data(url):
    try:
        response = requests.get(url, headers=WIKIDATA_API_HEADERS, timeout=10)
        logger.debug(f'{response.request.url}: {response.status_code}')
        return response, False
    except requests.exceptions.RequestException as e:
        logger.error(f'{e.__class__.__name__}: {e}')
        return response, True

def get_wikidata_statements(id):
    reponse, _ = get_wikidata_data(settings.WIKIDATA_STATEMENTS_URL.format(id))
    return reponse.json()


def get_wikidata_label(api_id: str, language_code: str= 'en') -> tuple[requests.Response, bool]:
    """Get the WikiData label"""
    url = settings.WIKIDATA_LABEL_URL.format(api_id, language_code)
    if not language_code and url.endswith('/'):
        url = url[:-1]

    return get_wikidata_data(url)

