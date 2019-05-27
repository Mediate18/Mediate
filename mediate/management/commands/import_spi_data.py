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

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Get the command line arguments
        database_path = kwargs['database_path']
        catalogue_ids_filename = kwargs['catalogue_ids_filename']

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

        dummy_collection, created = catalogues.models.Collection.objects.get_or_create(name='Dummy collection')

        # Catalogues
        catalogue_id_mapping = self.create_catalogues(dummy_collection, catalogue_ids, cursor)

        # Minimal Lot ID per Catalogue
        cursor.execute("SELECT catalogue_id, MIN(id) FROM `lot` GROUP BY catalogue_id")
        minimal_lot_id_per_catalogue = dict([
            (row['catalogue_id'], row['MIN(id)'])
            for row in cursor.fetchall()
        ])

        # Lots
        lot_id_mapping, lot_ids = self.create_lots(catalogue_id_mapping, catalogue_ids, cursor,
                                                   minimal_lot_id_per_catalogue)

        # Items
        self.create_items(cursor, dummy_collection, lot_id_mapping, lot_ids)

        # Close database connection
        cursor.close
        db_connection.close()

    def create_items(self, cursor, dummy_collection, lot_id_mapping, lot_ids):
        cursor.execute("SELECT `item`.*, `lot`.entry_text FROM `item` JOIN `lot` ON `item`.lot_id = `lot`.id "
                           "WHERE `lot`.id IN({})".format(",".join([str(id) for id in lot_ids])))
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
                place, created = persons.models.Place.objects.get_or_create(name=places_of_publication[0], cerl_id=None)
            else:
                place = None
            # print('place: ' + str(place))
            person, created = persons.models.Person.objects.get_or_create(short_name=row['publisher'],
                                     surname=row['publisher'],
                                     first_names='',
                                     sex='UNKNOWN')
            # print('person: ' + str(person) + " " + str(created))
            edition = items.models.Edition(year=date, place=place)
            edition.save()
            # print('edition: ' + str(edition))
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
                    'lot_id': lot_id_mapping[row['lot_id']],
                    'collection': dummy_collection,
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

    def create_lots(self, catalogue_id_mapping, catalogue_ids, cursor, minimal_lot_id_per_catalogue):
        lot_id_mapping = {}
        if catalogue_ids:
            cursor.execute("SELECT * FROM lot WHERE catalogue_id IN({})".format(",".join(catalogue_ids)))
        else:
            cursor.execute("SELECT * FROM lot")
        resultSet = cursor.fetchall()
        lot_ids = []
        for row in resultSet:
            try:
                lot_id = int(row['id'])
                lot_ids.append(lot_id)
                catalogue_id = int(row['catalogue_id'])
                index_in_catalogue = lot_id - minimal_lot_id_per_catalogue[catalogue_id] + 1
            except:
                index_in_catalogue = None
            try:
                page_in_catalogue = int(row['page_in_catalogue'])
            except:
                page_in_catalogue = None

            catalogue_id = catalogue_id_mapping[row['catalogue_id']]

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
            parent_category, created = catalogues.models.Category.objects.get_or_create(catalogue_id=catalogue_id,
                                              bookseller_category=parent) if parent else (None, None)

            category, created = catalogues.models.Category.objects.get_or_create(catalogue_id=catalogue_id,
                                       bookseller_category=child, parent=parent_category)

            insert_fields = {
                'catalogue_id': catalogue_id,
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
                lot_id_mapping[row['id']] = lot.pk
            except Exception as e:
                print(insert_fields)
                raise e

        return lot_id_mapping, lot_ids

    def create_catalogues(self, dummy_collection, catalogue_ids, cursor):
        catalogue_id_mapping = {}
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
                'collection': dummy_collection
            }

            try:
                catalogue = catalogues.models.Catalogue(**insert_fields)
                catalogue.save()
                catalogue_id_mapping[row['id']] = catalogue.pk
            except Exception as e:
                print(insert_fields)
                raise e

        return catalogue_id_mapping
