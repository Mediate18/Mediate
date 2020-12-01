"""
Checks and corrects
* index_in_catalogue for Lots
* index_in_lot for Items
"""


from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Max, F

from catalogues.models import Catalogue, Lot


class Command(BaseCommand):
    help = 'Check and correct indices'

    def __init__(self):
        self.dry_run = False

    def add_arguments(self, parser):
        # Positional
        parser.add_argument('catalogue', type=str, nargs='*', help='Catalogue UUID')

        # Optional
        parser.add_argument('-d', '--dry_run', action='store_true', help='Do not make any change to the database.')
        parser.add_argument('-vv', '--verbose', action='store_true', help='Print the data.')

    def correct_indices_in_catalogue(self, catalogue, indices_in_catalogue, start_index=1):
        # Keep track of the last index so determine duplicates
        last_index = start_index - 1

        gaps = []
        duplicates = False

        # Keep track of the total gap difference to select the correct index_in_catalogue
        # for subsequent updates
        total_diff = 0

        for index in indices_in_catalogue[start_index - 1:]:
            expected_index = last_index + 1 if last_index else 1
            if index == last_index:
                duplicates = True
                print("Duplicate =>", index)
            elif index > expected_index:
                print("Gap => expected: {}, real: {}".format(expected_index, index))
                diff = index - expected_index
                gaps.append((catalogue.uuid, index - total_diff, diff))
                total_diff += diff
            last_index = index

        # If there are gaps and no duplicates, just re-index
        if gaps and not duplicates:
            print("Re-indexing {} ({})".format(catalogue, catalogue.uuid))
            for gap in gaps:
                if self.dry_run:
                    print("Lot.objects.filter(catalogue__uuid={}, index_in_catalogue__gte={})"
                          ".update(index_in_catalogue=F('index_in_catalogue') - {}".format(gap[0], gap[1], gap[2]))
                else:
                    Lot.objects.filter(catalogue__uuid=gap[0], index_in_catalogue__gte=gap[1])\
                        .update(index_in_catalogue=F('index_in_catalogue') - gap[2])

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Get the command line arguments
        self.dry_run = kwargs["dry_run"]
        verbose = kwargs["verbose"]

        catalogue_uuids = kwargs.get('catalogue', [])

        catalogues_to_check = Catalogue.objects.filter(uuid__in=catalogue_uuids) if catalogue_uuids \
             else Catalogue.objects.all()

        incorrect_catalogues = []

        for catalogue in catalogues_to_check:
            # Get number of lots in this catalogue
            number_of_lots = Lot.objects.filter(catalogue=catalogue).count()
            # Get the index_in_catalogue max
            index_in_catalogue_max = Lot.objects.filter(catalogue=catalogue)\
                .aggregate(Max('index_in_catalogue'))['index_in_catalogue__max']

            # Get index_in_catalogue list
            lots = Lot.objects.filter(catalogue=catalogue)
            indices_in_catalogue = list(lots.values_list('index_in_catalogue', flat=True)
                                        .order_by('index_in_catalogue'))

            # Check whether the list of indices is the same as a generated list of 1 .. max
            if index_in_catalogue_max and indices_in_catalogue == list(range(1, index_in_catalogue_max + 1)):
                if verbose:
                    print("Catalogue {} ({}) is correct".format(catalogue, catalogue.uuid))
            elif number_of_lots == 0:
                if verbose:
                    print("Catalogue {} ({}) does not have any Lots".format(catalogue, catalogue.uuid))
            else:
                print("Catalogue {} ({}) is INCORRECT".format(catalogue, catalogue.uuid))
                incorrect_catalogues.append(catalogue)

                self.correct_indices_in_catalogue(catalogue, indices_in_catalogue)

        print("INCORRECT CATALOGUES ({}):".format(len(incorrect_catalogues)))
        for catalogue in incorrect_catalogues:
            print(catalogue, catalogue.uuid)
