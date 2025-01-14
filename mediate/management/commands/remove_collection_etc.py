from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Count
from catalogues.models import Collection, Category
from items.models import Item, Edition


class Command(BaseCommand):
    help = 'Removes a collection and related data'

    def add_arguments(self, parser):
        # Positional
        parser.add_argument('collection_id', type=str, help='ID (uuid) of the collection to delete')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        try:
            collection = Collection.objects.get(uuid=kwargs.get('collection_id', None))
        except ObjectDoesNotExist as e:
            print('No collection with id', kwargs['collection_id'])
            return

        print('Category:', Category.objects.filter(collection=collection).delete())

        catalogues = collection.catalogue.all()
        for catalogue in catalogues:
            items = Item.objects.filter(catalogue=catalogue)
            edition_ids = list(items.values_list('edition_id', flat=True))
            editions = Edition.objects.filter(uuid__in=edition_ids).annotate(item_count=Count('items')).filter(item_count=0)
            print('Item:', items.delete())
            print('Edition:', editions.delete())
        print('Catalogue:', catalogues.delete())

        print('Collection:', collection.delete())

