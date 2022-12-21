"""
Command to merge two collections in the order they are given.

What is actually done is move the lots and categories
of the second collection to the first.
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max, F
from django.db import transaction

from catalogues.models import CatalogueCollectionRelation, Collection, Lot, Category


def get_collections(collection__uuids):
    if len(collection__uuids) != 2:
        raise CommandError(f"You must give two collection IDs. {len(collection__uuids)} given")

    collections = []
    for i in range(2):
        try:
            collection = Collection.objects.get(uuid=collection__uuids[i])
            collections.append(collection)
        except ObjectDoesNotExist:
            raise CommandError(f"No collection found using ID {collection__uuids[i]}.")

    return collections

class Command(BaseCommand):
    help = 'Merge collections'

    def add_arguments(self, parser):
        # Positional
        parser.add_argument('collection_uuids', nargs='+', type=str)

    def handle(self, *args, **kwargs):
        # Get the command line arguments
        first_collection, second_collection = get_collections(kwargs.get('collection_uuids', []))

        # Get last index from first collection
        last_index = Lot.objects.filter(collection=first_collection)\
            .aggregate(Max("index_in_collection"))['index_in_collection__max']

        # Determine what to move
        lots_to_move = Lot.objects.filter(collection=second_collection)
        categories_to_move = Category.objects.filter(collection=second_collection)

        # Move stuff
        with transaction.atomic():
            lots_to_move.update(
                index_in_collection=F('index_in_collection') + last_index,
                collection=first_collection
            )

            categories_to_move.update(collection=first_collection)

            # Make sure the first collection is connected to the same catalogues as the second
            for catalogue in second_collection.catalogue.all():
                CatalogueCollectionRelation.objects.get_or_create(collection=first_collection, catalogue=catalogue)

            print("Full collection:", first_collection.get_absolute_url())
            print("Empty collection:", second_collection.get_absolute_url())
