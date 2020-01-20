"""
Match Persons to Items

"""


import re
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

    def normalize(self, string):
        return re.sub(r' +', ' ', string['short_title'].replace(":", ".").replace(",", ".").lower())

    # Yield successive n-sized
    # chunks from l.
    def divide_chunks(self, l, n):

        # looping till length l
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def duplicates(self, lst):
        seen = set()
        duplicates = []
        for t in lst:
            if t[1] in seen:
                duplicates.append(t[0])
            else:
                seen.add(t[1])

        return duplicates

    def do_matching(self, catalogue_ids):
        # Determine duplicate short_titles
        short_titles = [(item['uuid'], self.normalize(item))
                        for item in Item.objects.values('short_title', 'uuid')]

        print("#short_titles:", len(short_titles), short_titles[0])

        short_title_duplicates = self.duplicates(short_titles)

        print("#duplicates:", len(short_title_duplicates), len(set(short_title_duplicates)))

        total = 0

        for duplicate_chunk in self.divide_chunks(short_title_duplicates, 1000):

            duplicates_with_personitemrelations = Item.objects\
                .filter(uuid__in=duplicate_chunk)\
                .annotate(personitemrelation_cnt=Count('personitemrelation'))\
                .order_by()\
                .filter(personitemrelation_cnt__gt=0)

            print("#relations:", PersonItemRelation.objects.filter(item__uuid__in=duplicate_chunk).count())

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




