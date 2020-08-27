"""

"""

from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.models import F
from django.db import transaction

from catalogues.models import Collection, Catalogue, Lot, Category


def range_string_to_list(range_string):
    begin, end = range_string.split('-', 1)
    return list(range(int(begin), int(end) + 1))


def ranges_string_to_list(ranges_string):
    parts = ranges_string.split(',')
    numbers = set()

    for part in parts:
        if '-' in part:
            numbers.update(range_string_to_list(part))
        elif part:
            numbers.update(int(part))
    return sorted(list(numbers))


class Command(BaseCommand):
    help = 'Split catalogue'

    def add_arguments(self, parser):
        # Optional
        parser.add_argument('-c', '--catalogue_id', type=str,
                            help='UUID of catalogue to split')
        parser.add_argument('-n', '--new_catalogue_name', type=str,
                            help='Name of the new catalogue')
        parser.add_argument('-i', '--index_in_catalogue', type=int,
                            help='The index in the old catalogue of the first lot in the new catalogue')
        parser.add_argument('-e', '--exclude_index_in_catalogue', type=str,
                            help='Lots with these indexes are not move to the new catalogue')

    def handle(self, *args, **kwargs):
        # Get the command line arguments
        catalogue = Catalogue.objects.get(uuid=kwargs.get('catalogue_id'))
        lot = Lot.objects.get(catalogue=catalogue, index_in_catalogue=kwargs.get('index_in_catalogue'))
        new_catalogue_name = kwargs.get('new_catalogue_name')
        exclude_indexes = ranges_string_to_list(kwargs.get('exclude_index_in_catalogue') or '')
        if not (catalogue and lot and new_catalogue_name):
            return

        with transaction.atomic():
            new_collection = Collection.objects.create(name=new_catalogue_name)
            new_catalogue = Catalogue.objects.create(short_title=new_catalogue_name, collection=new_collection)
            print("New catalogue URL:", new_catalogue.get_absolute_url())
            lots_to_move = Lot.objects.filter(catalogue=catalogue, index_in_catalogue__gte=lot.index_in_catalogue)\
                            .exclude(index_in_catalogue__in=exclude_indexes)
            categories_to_move = Category.objects.filter(lot__in=lots_to_move).distinct()

            # Create new categories if necessary
            for category in categories_to_move.filter(lot__index_in_catalogue__lt=lot.index_in_catalogue):
                new_category = Category.objects.create(
                    catalogue = category.catalogue,
                    bookseller_category = category.bookseller_category,
                    parisian_category = category.parisian_category
                )
                lots_to_move.filter(category=category).update(category=new_category)

            diff = lot.index_in_catalogue - 1
            lots_to_move.update(catalogue=new_catalogue, index_in_catalogue=F('index_in_catalogue') - diff)
