"""
Match Persons to Items

"""


import re
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count, Q
from catalogues.models import Collection
from items.models import Item, PersonItemRelation


class Command(BaseCommand):
    help = 'Matches Persons to Items'

    def add_arguments(self, parser):
        # Optional
        parser.add_argument('-c', '--collection_ids_filename', type=str,
                            help='Path to a list of collection IDs to process (one ID per line)')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Get the command line arguments
        if 'collection_ids_filename' in kwargs:
            collection_ids_filename = kwargs['collection_ids_filename']

        # Read collection IDs
        collection_ids = []
        if collection_ids_filename:
            with open(collection_ids_filename, 'r') as cat_ids_file:
                collection_ids = [id.strip() for id in cat_ids_file.readlines()]

        print("#collection_ids:", len(collection_ids))
        print("#collections:", Collection.objects.filter(short_title__in=collection_ids).count())
        for collection_id in collection_ids:
            try:
                Collection.objects.get(short_title=collection_id)
            except:
                print("collection <{}> not found".format(collection_id))

        self.do_matching(collection_ids)

    def normalize(self, string):
        return re.sub(r' +', ' ', string.replace(":", ".").replace(",", ".").lower())

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

    def do_matching(self, collection_ids=None):
        """Matches normalized short_titles and copies the PersonItemRelations."""

        short_titles_with_relations = self.get_short_titles_with_relations()
        print("#short_titles_with_relations", len(short_titles_with_relations))

        filter = Q()
        if collection_ids:
            filter = Q(lot__collection__short_title__in=collection_ids)
        short_titles_target_items = self.get_short_titles_with_filter(filter)
        print("#short_titles_target_items", len(short_titles_target_items))

        # Find short_titles that are in both lists
        short_title_intersection = short_titles_with_relations.keys() & short_titles_target_items.keys()
        print("#short_title_intersection", len(short_title_intersection))
        total_items_with_copyable_relations = 0
        for short_title in short_title_intersection:
            total_items_with_copyable_relations += len(short_titles_with_relations[short_title])
        print("total_items_with_copyable_relations:", total_items_with_copyable_relations)

        # Copy PersonItemRelations to target items
        grand_total = 0

        for short_title in short_title_intersection:
            personitemrelations_to_copy = PersonItemRelation.objects\
                .filter(item_id__in=short_titles_with_relations[short_title])
            total_for_short_title = 0
            for relation_to_copy in personitemrelations_to_copy:
                for item_id in short_titles_target_items[short_title]:
                    relation, created = PersonItemRelation.objects.get_or_create(item_id=item_id,
                                                                        person=relation_to_copy.person,
                                                                        role=relation_to_copy.role)
                    if created:
                        total_for_short_title += 1
            print("Total for {}: {}".format(short_title, total_for_short_title))
            grand_total += total_for_short_title

        print("Grand total:", grand_total)

    def get_short_titles_with_filter(self, filter=None):
        """Get short_titles from items and filter them"""

        items_from_selected_collections = Item.objects \
            .values_list('short_title', 'uuid') \
            .annotate(personitemrelation_cnt=Count('personitemrelation')) \
            .order_by() \
            .filter(personitemrelation_cnt=0)
        if filter:
            items_from_selected_collections = items_from_selected_collections.filter(filter) \

        short_titles_from_selected_collections = defaultdict(list)
        for short_title, uuid, cnt in items_from_selected_collections:
            short_titles_from_selected_collections[self.normalize(short_title)].append(uuid)

        return short_titles_from_selected_collections

    def get_short_titles_with_relations(self):
        """Get short_titles from items that also have a relation to a person"""

        items_with_relations = Item.objects \
            .values_list('short_title', 'uuid') \
            .annotate(personitemrelation_cnt=Count('personitemrelation')) \
            .order_by() \
            .filter(personitemrelation_cnt__gt=0)

        short_titles_with_relations = defaultdict(list)
        for short_title, uuid, cnt in items_with_relations:
            short_titles_with_relations[self.normalize(short_title)].append(uuid)

        return short_titles_with_relations



