"""
Checks and corrects
* index_in_collection for Lots
* index_in_lot for Items
"""


from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Max, F

from catalogues.models import Collection, Lot


class Command(BaseCommand):
    help = 'Check and correct indices'

    def __init__(self):
        self.dry_run = False

    def add_arguments(self, parser):
        # Positional
        parser.add_argument('collection', type=str, nargs='*', help='Collection UUID')

        # Optional
        parser.add_argument('-d', '--dry_run', action='store_true', help='Do not make any change to the database.')
        parser.add_argument('-vv', '--verbose', action='store_true', help='Print the data.')

    def correct_indices_in_collection(self, collection, indices_in_collection, start_index=1):
        # Keep track of the last index so determine duplicates
        last_index = start_index - 1

        gaps = []
        duplicates = False

        # Keep track of the total gap difference to select the correct index_in_collection
        # for subsequent updates
        total_diff = 0

        for index in indices_in_collection[start_index - 1:]:
            expected_index = last_index + 1 if last_index else 1
            if index == last_index:
                duplicates = True
                print("Duplicate =>", index)
            elif index > expected_index:
                print("Gap => expected: {}, real: {}".format(expected_index, index))
                diff = index - expected_index
                gaps.append((collection.uuid, index - total_diff, diff))
                total_diff += diff
            last_index = index

        # If there are gaps and no duplicates, just re-index
        if gaps and not duplicates:
            print("Re-indexing {} ({})".format(collection, collection.uuid))
            for gap in gaps:
                if self.dry_run:
                    print("Lot.objects.filter(collection__uuid={}, index_in_collection__gte={})"
                          ".update(index_in_collection=F('index_in_collection') - {}".format(gap[0], gap[1], gap[2]))
                else:
                    Lot.objects.filter(collection__uuid=gap[0], index_in_collection__gte=gap[1])\
                        .update(index_in_collection=F('index_in_collection') - gap[2])

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Get the command line arguments
        self.dry_run = kwargs["dry_run"]
        verbose = kwargs["verbose"]

        collection_uuids = kwargs.get('collection', [])

        collections_to_check = Collection.objects.filter(uuid__in=collection_uuids) if collection_uuids \
             else Collection.objects.all()

        incorrect_collections = []

        for collection in collections_to_check:
            # Get number of lots in this collection
            number_of_lots = Lot.objects.filter(collection=collection).count()
            # Get the index_in_collection max
            index_in_collection_max = Lot.objects.filter(collection=collection)\
                .aggregate(Max('index_in_collection'))['index_in_collection__max']

            # Get index_in_collection list
            lots = Lot.objects.filter(collection=collection)
            indices_in_collection = list(lots.values_list('index_in_collection', flat=True)
                                        .order_by('index_in_collection'))

            # Check whether the list of indices is the same as a generated list of 1 .. max
            if index_in_collection_max and indices_in_collection == list(range(1, index_in_collection_max + 1)):
                if verbose:
                    print("Collection {} ({}) is correct".format(collection, collection.uuid))
            elif number_of_lots == 0:
                if verbose:
                    print("Collection {} ({}) does not have any Lots".format(collection, collection.uuid))
            else:
                print("Collection {} ({}) is INCORRECT".format(collection, collection.uuid))
                incorrect_collections.append(collection)

                self.correct_indices_in_collection(collection, indices_in_collection)

        print("INCORRECT CATALOGUES ({}):".format(len(incorrect_collections)))
        for collection in incorrect_collections:
            print(collection, collection.uuid)
