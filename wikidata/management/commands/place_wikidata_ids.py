import csv

import requests
from datetime import datetime, timedelta
from time import sleep
from django.core.management.base import BaseCommand
from django.conf import settings
from requests import JSONDecodeError

from persons.models import Place
from wikidata.utils import get_nested_object
from wikidata.views import request_wikidata_suggest

REQUEST_TIME_DIFF = 0.4
REQUEST_TIME_DELTA = timedelta(seconds=REQUEST_TIME_DIFF)


class Command(BaseCommand):
    help = "Find Wikidata IDs using Wikidata API for Places"
    header = [
        "Place ID",
        "Current place name",
        "Wikidata name",
        "Wikidata description",
        "Wikidata ID (Ctrl+click to open)",
        "Correct Wikidata ID",
    ]

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.last_request_time = datetime.now() - REQUEST_TIME_DELTA

    def add_arguments(self, parser):
        parser.add_argument("filename", nargs=1)

    def create_row(self, place, wikidata):
        return [
            place.pk,
            place.name,
            get_nested_object(wikidata, ('display-label', 'value'), ''),
            get_nested_object(wikidata, ('description', 'value'), ''),
            f'=HYPERLINK("{settings.WIKIDATA_URL.format(wikidata.get('id'))}";"{wikidata.get('id')}")',
            wikidata.get('id'),
        ]

    def get_response(self, name):
        # Wait a little to avoid Wikidata throttling errors
        new_request_time = datetime.now()
        time_diff = new_request_time - self.last_request_time
        if time_diff < REQUEST_TIME_DELTA:
            time_delta = REQUEST_TIME_DELTA - time_diff
            sleep(time_delta.total_seconds())
        self.last_request_time = new_request_time

        response = request_wikidata_suggest(name, 1, 1)
        if response.status_code in [403, 429]:
            print(f"Responseo not ok, exiting: {name} {response.status_code} {response.text}")
            exit
        if response.status_code != requests.codes.ok:
            print(f"Response not ok: {name} {response.status_code} {response.text}")
            return None
        if response.headers['content-type'] != 'application/json':
            print(f"Response not JSON: {name} {response.text}")
            return None
        return response

    def sanitize_string(self, string):
        return string[:string.find(' (')]

    def handle(self, *args, **options):
        self.filename = options.get('filename', False)[0]
        with open(self.filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(self.header)
            for place in Place.objects.filter(wikidata_id='').exclude(name=''):
                response = self.get_response(place.name)
                if response is None:
                    continue
                results = response.json().get('results')
                if not results or type(results) is not list or type(results[0]) is not dict:
                    # Try with a sanitize version Place.name
                    response = self.get_response(self.sanitize_string(place.name))
                    results = response.json().get('results')
                    if not results or type(results) is not list or type(results[0]) is not dict:
                        print(f"Unusable results: {place} {results} {response.text}")
                        continue
                csvwriter.writerow(self.create_row(place, results[0]))
