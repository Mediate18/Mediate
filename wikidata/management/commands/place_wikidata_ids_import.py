import csv
import pprint

from datetime import datetime, timedelta
from time import sleep
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from persons.models import Place, Country
from wikidata.utils import get_nested_object
from wikidata.views import get_option_from_wikidata_property
from wikidata.wikidata_api import get_wikidata_statements

REQUEST_TIME_DIFF = 0.4
REQUEST_TIME_DELTA = timedelta(seconds=REQUEST_TIME_DIFF)


class Command(BaseCommand):
    help = "Import Wikidata IDs and other data using Wikidata API for Places"

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.last_request_time = datetime.now() - REQUEST_TIME_DELTA

    def add_arguments(self, parser):
        parser.add_argument("filename", nargs=1)

    def throttle(self):
        # Wait a little to avoid Wikidata throttling errors
        new_request_time = datetime.now()
        time_diff = new_request_time - self.last_request_time
        if time_diff < REQUEST_TIME_DELTA:
            time_delta = REQUEST_TIME_DELTA - time_diff
            sleep(time_delta.total_seconds())
        self.last_request_time = new_request_time

    def sanitize_string(self, string):
        return string[:string.find(' (')]

    def handle(self, *args, **options):
        self.filename = options.get('filename', False)[0]
        with open(self.filename, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            place_list = list(csvreader)

        for place_row in place_list[1:]:
            try:
                place = Place.objects.get(pk=place_row[0])
            except Place.DoesNotExist:
                print(f'No Place with id {place_row[0]}')
                continue

            place.name = place_row[2]
            place.wikidata_id = place_row[5]

            self.throttle()
            if data := get_wikidata_statements(place_row[5]):
                country_id = get_option_from_wikidata_property(data, 'P17', Country).get('id', None)
                place.country = Country.objects.filter(pk=country_id).first()
                latitude = get_nested_object(data, ('statements', 'P625', 0, 'value', 'content', 'latitude'), None)
                place.latitude = round(latitude, 6) if latitude else None
                longitude = get_nested_object(data, ('statements', 'P625', 0, 'value', 'content', 'longitude'), None)
                place.longitude = round(longitude, 6) if longitude else None

            try:
                place.save()
            except IntegrityError as e:
                print(e)

