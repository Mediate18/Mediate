"""
Import SPi data from an existing database

1. Transform the MySQL data from SPi to SQLite
  - git clone https://github.com/dumblob/mysql2sqlite
  - mysqldump --skip-extended-insert --compact -u <user> -p <database > output.sql
  - ./mysql2sqlite/mysql2sqlite output.sql > sqlite_db.sql
  - sqlite3 sqlite_db.db < sqlite_db.sql
2. Run this script as manage.py command
"""

from django.core.management.base import BaseCommand
from django.db import transaction
import sqlite3
import re
import catalogues
import items
import persons


class Command(BaseCommand):
    help = 'Imports SPi data from an SQLite database'

    def add_arguments(self, parser):
        # Positional
        parser.add_argument('database_path', type=str, help='Path to the SQLite database containing SPi data')

        # Optional
        parser.add_argument('-c', '--catalogue_ids_filename', type=str,
                            help='Path to a list of catalogue IDs to process (one ID per line)')
        parser.add_argument('-m', '--multiple_catalogues_per_collection_tmp',
                            action='store_true',
                            help='Allow for multiple catalogues per collection_tmp')
        parser.add_argument('-d', '--dataset_name', type=str,
                            help='Name of the dataset the collection_tmp/catalogue must put into')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Get the command line arguments
        database_path = kwargs['database_path']
        catalogue_ids_filename = kwargs['catalogue_ids_filename']
        self.multiple_catalogues_per_collection_tmp = kwargs.get('multiple_catalogues_per_collection_tmp', False)
        self.dataset_name = kwargs.get('dataset_name', "Dump")

        # Read catalogue IDs
        if catalogue_ids_filename:
            with open(catalogue_ids_filename, 'r') as cat_ids_file:
                catalogue_ids = [id.strip() for id in cat_ids_file.readlines()]

        # Open database connections
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        db_connection = sqlite3.connect(database_path)
        db_connection.row_factory = dict_factory
        cursor = db_connection.cursor()

        # Catalogues
        catalogue_id_mapping = self.create_catalogues(catalogue_ids, cursor)

        # Close database connection
        cursor.close
        db_connection.close()

    def create_items(self, lot, lot_spi_id, cursor):
        cursor.execute("SELECT `item`.*, `lot`.entry_text FROM `item` JOIN `lot` ON `item`.lot_id = `lot`.id "
                           "WHERE `lot`.id = {}".format(lot_spi_id))
        resultSet = cursor.fetchall()
        for row in resultSet:
            places_of_publication = re.compile(r'\/').split(row['place_of_publication'])
            # print('places_of_publication: ' + str(places_of_publication))

            dates_of_publication = re.compile(r'\/').split(row['date_of_publication'])
            # print('dates_of_publication: ' + str(dates_of_publication))
            date = dates_of_publication[0] if dates_of_publication and dates_of_publication[0] else None
            try:
                date = int(date)
            except:
                date = None
            # print('date: ' + str(date))

            if places_of_publication and places_of_publication[0]:
                # Find a place marked with [non-CERL]
                non_cerl_str = "[non-CERL]"
                place_name = places_of_publication[0]
                places = persons.models.Place.objects\
                    .filter(name__iregex=re.escape(place_name) + r' +' + re.escape(non_cerl_str))
                if places:
                    place = places[0]
                else:
                    place = persons.models.Place.objects.create(name="{} {}".format(place_name, non_cerl_str))
            else:
                place = None
            # print('place: ' + str(place))
            if row['publisher']:
                person, created = persons.models.Person.objects.get_or_create(short_name=row['publisher'],
                                         surname=row['publisher'],
                                         first_names='',
                                         sex='UNKNOWN')
            else:
                person = None
            # print('person: ' + str(person) + " " + str(created))
            edition = items.models.Edition(year_start=date, place=place)
            edition.save()
            # print('edition: ' + str(edition))
            if person:
                publisher = items.models.Publisher(edition=edition, publisher=person)
                publisher.save()
                # print('publisher: ' + str(publisher))

            item_entries = re.compile(r'\s?\/\s?').split(row['entry_text'])
            if len(item_entries) >= row['index_in_lot']:
                short_title = item_entries[row['index_in_lot'] - 1]
            else:
                short_title = ""

            try:
                book_format = None
                if row['book_format']:
                    book_format, created = items.models.BookFormat.objects.get_or_create(name=row['book_format'])
                insert_fields = {
                    'short_title': short_title[:128],
                    'lot': lot,
                    'collection_tmp': lot.catalogue.collection_tmp,
                    'number_of_volumes': row['number_of_volumes'],
                    'book_format': book_format,
                    'index_in_lot': row['index_in_lot'],
                    'edition_id': edition.uuid,
                }
            except Exception as e:
                print(str(row))
                print(str(item_entries))
                raise e

            try:
                item = items.models.Item(**insert_fields)
                item.save()
            except Exception as e:
                print(insert_fields)
                raise e

            if row['binding_material_details']:
                material_details, created = items.models.MaterialDetails.objects.get_or_create(
                    description=row['binding_material_details'])
                item_materialdetails_relations = items.models.ItemMaterialDetailsRelation(item=item,
                                                                                          material_details=material_details)
                item_materialdetails_relations.save()

    def create_lots(self, catalogue, catalogue_spi_id, cursor):
        minimal_lot_id = cursor.execute("SELECT MIN(ID) FROM lot WHERE catalogue_id={}".format(catalogue_spi_id))\
            .fetchall()[0]['MIN(ID)']

        query = "SELECT * FROM lot WHERE `catalogue_id` = {}".format(catalogue_spi_id)
        cursor.execute(query)
        resultSet = cursor.fetchall()
        lot_ids = []
        for row in resultSet:
            try:
                lot_id = int(row['id'])
                lot_ids.append(lot_id)
                index_in_catalogue = lot_id - minimal_lot_id + 1
            except:
                index_in_catalogue = None
            try:
                page_in_catalogue = int(row['page_in_catalogue'])
            except:
                page_in_catalogue = None

            bookseller_category = row['bookseller_category_books']

            # Try to match 'MAIN CATEGORY \ SUB CATEGORY [MAIN CATEGORY]',
            # 'SUB CATEGORY [MAIN CATEGORY]' or 'MAIN CATEGORY \ SUB CATEGORY'
            match = re.match(r'^(([^\\]+?) ?\\ ?)?([^\[]+)( \[([^\]]+)\])?$', bookseller_category)
            if match:
                parent = match.groups()[1] or match.groups()[4]
                child = match.groups()[2]
            else:
                # No main and sub category
                parent = None
                child = bookseller_category

            # Link to Category
            parent_category, created = catalogues.models.Category.objects.get_or_create(catalogue=catalogue,
                                              bookseller_category=parent) if parent else (None, None)

            category, created = catalogues.models.Category.objects.get_or_create(catalogue=catalogue,
                                       bookseller_category=child, parent=parent_category)

            insert_fields = {
                'catalogue': catalogue,
                'category': category,
                'number_in_catalogue': row['number_in_catalogue'],
                'lot_as_listed_in_catalogue': row['entry_text'],
                'sales_price': row['sales_price'][:128],
                'page_in_catalogue': page_in_catalogue,
                'index_in_catalogue': index_in_catalogue
            }

            try:
                lot = catalogues.models.Lot(**insert_fields)
                lot.save()
                self.create_items(lot, row['id'], cursor)
            except Exception as e:
                print(insert_fields)
                raise e

    def create_catalogues(self, catalogue_ids, cursor):
        if catalogue_ids:
            query = "SELECT * FROM catalogue WHERE id IN({})".format(",".join(catalogue_ids))
        else:
            query = "SELECT * FROM catalogue"
        cursor.execute(query)
        resultSet = cursor.fetchall()

        for row in resultSet:
            insert_fields = {
                'short_title': row['short_title'],
                'full_title': row['full_title'],
                'preface_and_paratexts': row['preface_and_paratexts'],
            }

            try:
                # Only use a collection_tmp that is new or that does not have any catalogues linked to it.
                collection_tmp, created = catalogues.models.Collection_TMP.objects.get_or_create(name=row['short_title'])
                if created:
                    collection_tmp.dataset = catalogues.models.Dataset.objects.get(name=self.dataset_name)
                    collection_tmp.save()
                else:
                    if collection_tmp.catalogue_set.count() != 0 and not self.multiple_catalogues_per_collection_tmp:
                        raise Exception("Collection_TMP {} already exists and has catalogues linked to.".format(collection_tmp))

                catalogue = catalogues.models.Catalogue(**insert_fields)
                catalogue.collection_tmp = collection_tmp
                catalogue.save()
                self.create_lots(catalogue, row['id'], cursor)
            except Exception as e:
                print(insert_fields)
                raise e
