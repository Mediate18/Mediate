"""
Match Persons to Items

"""


from django.core.management.base import BaseCommand
from django.db import transaction
from catalogues.models import Catalogue
from items.models import Item, PersonItemRelation


class Command(BaseCommand):
    help = 'Matches Persons to Items'

    def add_arguments(self, parser):
        # Optional
        parser.add_argument('-c', '--catalogue_ids_filename', type=str,
                            help='Path to a list of catalogue IDs to process (one ID per line)')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Get the command line arguments
        catalogue_ids_filename = kwargs['catalogue_ids_filename']

        # Read catalogue IDs
        if catalogue_ids_filename:
            with open(catalogue_ids_filename, 'r') as cat_ids_file:
                catalogue_ids = [id.strip() for id in cat_ids_file.readlines()]

        total_new = 0
        for catalogue_id in catalogue_ids:
            catalogue = Catalogue.objects.get(short_title=catalogue_id)
            total_new += self.do_matching(catalogue)

        print("total_new:", total_new)

    def do_matching(self, catalogue):
        items = Item.objects.filter(lot__catalogue=catalogue)
        total_new = 0
        for item in items:
            # matched_items = Item.objects.exclude(lot__catalogue=catalogue).filter(short_title=item.short_title)
            personitemrelations = PersonItemRelation.objects.filter(item__short_title=item.short_title)\
                .exclude(item=item)
            # for relation in personitemrelations:
            #     PersonItemRelation(item=item, person=relation.person, role=relation.role).save()
            number_of_new = personitemrelations.count()
            if number_of_new > 0:
                print("number_of_new", number_of_new)
                total_new += number_of_new

        return total_new

