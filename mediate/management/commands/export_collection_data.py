from django.core.management.base import BaseCommand
import csv
import sys
from items.models import Item, MaterialDetails, Language, ItemType
from persons.models import Person, Place


class Command(BaseCommand):
    help = 'Exports data for a Collection'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dry_run = False

    def add_arguments(self, parser):
        # Positional
        parser.add_argument('collection', type=str, nargs='*', help='Collection UUID')

        # Optional
        # parser.add_argument('-d', '--dry_run', action='store_true', help='Do not make any change to the database.')
        # parser.add_argument('-vv', '--verbose', action='store_true', help='Print the data.')

    def get_edition_string(self, item):
        year = item.edition.get_year_range_str()
        year_str = year if year else ""
        publishers_str = ", ".join(
            Person.objects.filter(publisher__edition=item.edition_id).values_list('short_name', flat=True)
        )
        places_str = ", ".join(
            Place.objects.filter(publicationplace__edition=item.edition_id).values_list('name', flat=True)
        )
        return f'{places_str}{": " if places_str else ""}{publishers_str}{", " if publishers_str and year_str else ""}{year_str}'

    def handle(self, *args, **kwargs):
        collection_uuids = kwargs.get('collection', [])

        writer = csv.writer(sys.stdout)
        for collection_uuid in collection_uuids:
            # Items
            writer.writerow(["Short title", "People VIAF", "Work VIAF", "Lot", "Index in lot", "Collection",
                             "Number of volumes", "Book format", "Material details", "Edition", "Languages",
                             "Parisian category", "Item type", "Tags"])
            for item in Item.objects.filter(lot__collection_id=collection_uuid):
                writer.writerow([
                    item.short_title,
                    "; ".join(Person.objects.exclude(viaf_id__isnull=True).filter(personitemrelation__item=item).values_list('viaf_id', flat=True)),
                    "; ".join(relation.work.viaf_id for relation in item.works.all() if relation.work.viaf_id),
                    item.lot.lot_as_listed_in_collection,
                    item.index_in_lot,
                    item.lot.collection.short_title,
                    item.number_of_volumes,
                    item.book_format.name if item.book_format else "",
                    "; ".join(MaterialDetails.objects.filter(items__item=item).values_list('description', flat=True)),
                    self.get_edition_string(item),
                    "; ".join(Language.objects.filter(items__item=item).values_list('name', flat=True)),
                    item.parisian_category.name if item.parisian_category else "",
                    "; ".join(ItemType.objects.filter(itemitemtyperelation__item=item).values_list('name', flat=True)),
                    ", ".join([str(taggedentity.tag) for taggedentity in item.tags.all()])
                ])
