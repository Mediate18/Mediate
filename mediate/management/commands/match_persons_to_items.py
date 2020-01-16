"""
Match Persons to Items

"""


from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count, Subquery
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

        print("#catalogue_ids:", len(catalogue_ids))
        print("#catalogues:", Catalogue.objects.filter(short_title__in=catalogue_ids).count())
        for catalogue_id in catalogue_ids:
            try:
                Catalogue.objects.get(short_title=catalogue_id)
            except:
                print("catalogue <{}> not found".format(catalogue_id))

        self.do_matching(catalogue_ids)

    def do_matching(self, catalogue_ids):
        short_title_duplicates = Item.objects\
            .values_list('short_title', flat=True)\
            .annotate(short_title_cnt=Count('short_title'))\
            .order_by()\
            .filter(short_title_cnt__gt=1)
        duplicates_with_personitemrelations = Item.objects\
            .filter(short_title__in=Subquery(short_title_duplicates.values('short_title')))\
            .annotate(personitemrelation_cnt=Count('personitemrelation'))\
            .order_by()\
            .filter(personitemrelation_cnt__gt=0)

        total = 0

        for source_item in duplicates_with_personitemrelations:
            personitemrelations_to_copy = PersonItemRelation.objects.filter(item=source_item)

            relation_count = personitemrelations_to_copy.count()
            # print("Count:", relation_count)
            total += relation_count

            # for target_item in Item.objects.filter(short_title=source_item.short_title,
            #                                        lot__catalogue__short_title__in=catalogue_ids):
                # for relation in personitemrelations_to_copy:
                #     PersonItemRelation(item=target_item, person=relation.person, role=relation.role).save()

        print("Total:", total)




