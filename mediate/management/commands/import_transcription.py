"""
Import text transcriptions
"""

import os
import re
from collections import OrderedDict
from django.core.management.base import BaseCommand
from django.db import transaction
from django.forms.models import model_to_dict
from catalogues.models import Collection, Catalogue, Lot, Category
from items.models import Item, Edition
from persons.models import Place


class Command(BaseCommand):
    help = 'Imports text transcriptions'

    def add_arguments(self, parser):
        # Positional
        parser.add_argument('transcription', type=str, nargs='+', help='Text transcription file')

        # Optional
        parser.add_argument('-d', '--dry_run', action='store_true', help='Do not save to database, but print the data.')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Get the command line arguments
        transcription_files = kwargs['transcription']
        dry_run = kwargs["dry_run"]

        markers = OrderedDict({
            "TITLE": "TIT@",
            "PREFACE": "PRE@",
            "CATEGORY": "CAT@",
            "OTHER": "OTH@",
            "ANNOTATION": "ANN@",
            "ITEM_NUMBER": "N@",
            "FULL_ITEM_DESC": "TT@",
            "LANGUAGE": "L@",
            "AUTHOR": "A@",
            "CITY": "C@",
            "PUBLISHER": "P@",
            "SHORT_TITLE": "T@",
            "YEAR": "Y@",
            "VOLUME": "V@",
            "EDITION": "E@",
            "FORMAT": "F@",
            "MATERIAL_DETAILS": "M@",
            "TRANSLATOR": "R@",
            "QUANTITY": "Q@",
            "SALES_PRICE": "S@",
            "BUYER": "B@",
            "HAND_COPIED_DETAILS": "H@",
            "ILLUSTRATOR": "I@",
            "FULL_ITEM_DESC_OTHER": "D@",
            "PAGE": "<>"
        })

        field_marker = "[--FIELD-MARKER-FOR-SPLITING--]"

        def add_field_marker(text):
            for name, marker in markers.items():
                text = re.sub(r'^'+marker, field_marker+marker, text)
                text = re.sub(r'(?<=\n)'+marker, field_marker+marker, text)
                text = re.sub(r'(?<=\r)'+marker, field_marker+marker, text)
            return text

        def save_or_print(obj, dry_run=False):
            if dry_run:
                print("{}: {}".format(obj.__class__.__name__, model_to_dict(obj)))
            else:
                obj.save()

        def fill_slots(fields):
            slots = {}
            for field in fields:
                for name, marker in markers.items():
                    if field.startswith(marker):
                        slots[name] = field[len(marker):].strip()
            return slots

        for file in transcription_files:
            # Take catalogue short_title from filename
            catalogue_short_title = os.path.splitext(os.path.basename(file))[0]

            collection = Collection(name=catalogue_short_title)
            save_or_print(collection, dry_run)

            with open(file, 'r', encoding='utf-8') as transcription:
                transcription_with_field_markers = add_field_marker(transcription.read())
                # print(transcription_with_field_markers)
                records = [record.strip() for record in transcription_with_field_markers.split("<%%>")]
                page = 0
                index_in_catalogue = 1
                catalogue = None
                for record in records:
                    # print(record)
                    fields = fill_slots(record.split(field_marker))
                    # print(fields)
                    if "PAGE" in fields:
                        page += 1
                    elif "TITLE" in fields:
                        title = fields["TITLE"]
                        catalogue = Catalogue(short_title=catalogue_short_title, full_title=title,
                                              collection=collection)
                        save_or_print(catalogue, dry_run)
                    elif "CATEGORY" in fields:
                        # print(fields)
                        category_books = fields["CATEGORY"]
                        category = Category(catalogue=catalogue, bookseller_category=category_books)
                        save_or_print(category, dry_run)
                    elif "FULL_ITEM_DESC" in fields:
                        full_item_desc_books = fields["FULL_ITEM_DESC"]
                        page_in_catalogue = page if page else None

                        # Lot
                        # TODO use get_or_create instead of the following:
                        lot = Lot(catalogue=catalogue,
                                  number_in_catalogue=fields.get("ITEM_NUMBER", None),
                                  page_in_catalogue=page_in_catalogue,
                                  sales_price=fields.get("SALES_PRICE", None),
                                  lot_as_listed_in_catalogue=full_item_desc_books,
                                  index_in_catalogue=index_in_catalogue,
                                  category=category)
                        save_or_print(lot, dry_run)
                        index_in_catalogue += 1

                        # Place
                        if "CITY" in fields:
                            non_cerl_str = "[non-CERL]"
                            place_name = fields.get("CITY")
                            places = Place.objects.filter(name__iregex=re.escape(place_name) + r' +'
                                                                       + re.escape(non_cerl_str))
                            if places:
                                place = places[0]
                            else:
                                place = Place.objects.create(name="{} {}".format(place_name, non_cerl_str))
                        else:
                            place = None

                        # Edition
                        if "YEAR" in fields:
                            try:
                                year = int(fields.get("YEAR"))
                                year_tag = None
                            except:
                                year = None
                                year_tag = fields.get("YEAR")
                        else:
                            year = None
                            year_tag = None

                        edition = Edition(place=place, year=year, year_tag=year_tag)
                        save_or_print(edition, dry_run)

                        # Format
                        if "FORMAT" in fields:
                            # TODO use get_or_create instead of the following:
                            book_format = BookFormat(name=fields.get("FORMAT"))
                            save_or_print(book_format, dry_run)
                        else:
                            book_format = None

                        # Item
                        item = Item(short_title=fields.get("FULL_ITEM_DESC")[:128],
                                    lot=lot,
                                    number_of_volumes=fields.get("VOLUME", None),
                                    book_format=book_format,
                                    index_in_lot=1,
                                    edition=edition)
                        save_or_print(item, dry_run)

                    elif "PREFACE" in fields:
                        catalogue.preface_and_paratexts = fields.get("PREFACE")
                        save_or_print(catalogue, dry_run)


