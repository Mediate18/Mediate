"""
Import text transcriptions
"""

import os
import re
from collections import OrderedDict
from django.core.management.base import BaseCommand
from django.db import transaction
from django.forms.models import model_to_dict
from catalogues.models import Catalogue, Collection, Lot, Category, Dataset
from items.models import Item, Edition, BookFormat, PublicationPlace
from persons.models import Place


CITY_NAME_SHORTHANDS = {'Lond.': 'London', 'Dubl.': 'Dublin', 'Edinb.': 'Edinburgh'}
MARKERS = OrderedDict({
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
FIELD_MARKER = "[--FIELD-MARKER-FOR-SPLITING--]"


class DryRunException(Exception):
    pass


def add_field_marker(text):
    for name, marker in MARKERS.items():
        text = re.sub(r'^'+marker, FIELD_MARKER+marker, text)
        text = re.sub(r'(?<=\n)'+marker, FIELD_MARKER+marker, text)
        text = re.sub(r'(?<=\r)'+marker, FIELD_MARKER+marker, text)
    return text


def print_obj(obj, verbose):
    if verbose:
        print("{}: {}".format(obj.__class__.__name__, model_to_dict(obj)))
    else:
        print(".", end="")


def fill_slots(fields):
    slots = {}
    for field in fields:
        for name, marker in MARKERS.items():
            if field.startswith(marker):
                slots[name] = field[len(marker):].strip()
    return slots


def find_matches(text: str, search_strings: list[str]) -> list[str]:
    joined_escaped_search_strings = "|".join([re.escape(n) for n in search_strings])
    return re.findall(f'({joined_escaped_search_strings})', text)


class Command(BaseCommand):
    help = 'Imports text transcriptions'

    def add_arguments(self, parser):
        # Positional
        parser.add_argument('transcription', type=str, nargs='+', help='Text transcription file')
        parser.add_argument('dataset', type=str, help='Dataset name')

        # Optional
        parser.add_argument('-d', '--dry_run', action='store_true', help='Do not save to database.')
        parser.add_argument('-vv', '--verbose', action='store_true', help='Print the data.')
        parser.add_argument('-n', '--newline_splitter', type=int, default=None,
                            help='Use newline as splitter instead of special string "<%%>".')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Get the command line arguments
        transcription_files = kwargs['transcription']
        dataset_name = kwargs['dataset']
        dry_run = kwargs["dry_run"]
        verbose = kwargs["verbose"]
        newline_splitter = kwargs["newline_splitter"]

        try:
            dataset = Dataset.objects.get(name=dataset_name)
        except Dataset.DoesNotExist as dne:
            print(f"Dataset '{dataset_name}' does not exist.")
            return

        for file in transcription_files:
            # Take collection short_title from filename
            collection_short_title = os.path.splitext(os.path.basename(file))[0]

            try:
                with open(file, 'r', encoding='utf-8') as transcription_file:
                    with transaction.atomic():
                        catalogue = Catalogue(name=collection_short_title, dataset=dataset)
                        print_obj(catalogue, verbose)
                        catalogue.save()

                        transcription = transcription_file.read().replace(u'\ufeff', '')
                        transcription_with_field_markers = add_field_marker(transcription)
                        # print(transcription_with_field_markers)
                        splitter = "\n" * newline_splitter if newline_splitter else "<%%>"
                        records = [record.strip() for record in transcription_with_field_markers.split(splitter)]
                        page = 0
                        index_in_collection = 1
                        collection = None

                        def get_collection(collection):
                            if not collection:
                                print("Creating a new collection")
                                collection =  Collection.objects.create(short_title=collection_short_title,
                                                                        full_title=collection_short_title)
                                collection.catalogue.add(catalogue)
                            return collection

                        category = None
                        for record in records:
                            if verbose:
                                print('---')  # Start of record
                            # print(record)

                            fields = fill_slots(record.split(FIELD_MARKER))
                            if "PAGE" in fields:
                                page_str = fields["PAGE"].strip()
                                page = int(page_str) if page_str.isdigit() else None
                                if verbose:
                                    print("Page", page)
                            if "TITLE" in fields:
                                title = fields["TITLE"]
                                collection = Collection(short_title=collection_short_title, full_title=title)
                                print_obj(collection, verbose)
                                collection.save()
                                collection.catalogue.add(catalogue)
                            if "CATEGORY" in fields:
                                # print(fields)
                                category_books = fields["CATEGORY"]
                                collection = get_collection(collection)
                                category = Category(collection=collection, bookseller_category=category_books)
                                print_obj(category, verbose)
                                category.save()
                            if "FULL_ITEM_DESC" in fields:
                                full_item_desc_books = fields["FULL_ITEM_DESC"]
                                page_in_collection = page if page else None

                                # Lot
                                collection = get_collection(collection)
                                lot, created = Lot.objects.get_or_create(collection=collection,
                                          number_in_collection=fields.get("ITEM_NUMBER", '-1'),
                                          page_in_collection=page_in_collection,
                                          sales_price=fields.get("SALES_PRICE", ""),
                                          lot_as_listed_in_collection=full_item_desc_books,
                                          index_in_collection=index_in_collection,
                                          category=category)
                                print_obj(lot, verbose)
                                lot.save()
                                index_in_collection += 1

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
                                elif matches := find_matches(full_item_desc_books, CITY_NAME_SHORTHANDS):
                                    full_place_name = CITY_NAME_SHORTHANDS[matches[0]]
                                    try:
                                        place = Place.objects.get(name=full_place_name)
                                        print_obj(place, verbose)
                                    except Place.DoesNotExist:
                                        place = None
                                else:
                                    place = None

                                # Edition
                                if "YEAR" in fields:
                                    try:
                                        year = int(fields.get("YEAR"))
                                        year_tag = ""
                                    except:
                                        year = None
                                        year_tag = fields.get("YEAR")
                                elif match := re.search(r'\d{4}', full_item_desc_books):
                                    year = int(match[0])
                                    year = year if year <= 1850 else None
                                    year_tag = ""
                                else:
                                    year = None
                                    year_tag = ""

                                edition = Edition(place=place, year_start=year, year_tag=year_tag)
                                print_obj(edition, verbose)
                                edition.save()

                                # PublicationPlace
                                if place:
                                    PublicationPlace.objects.create(place=place, edition=edition)

                                # Format
                                if "FORMAT" in fields:
                                    book_format, created = BookFormat.objects.get_or_create(name=fields.get("FORMAT"))
                                    print_obj(book_format, verbose)
                                else:
                                    book_format = None

                                # Item
                                item = Item(short_title=fields.get("FULL_ITEM_DESC")[:128],
                                            lot=lot,
                                            number_of_volumes=fields.get("VOLUME", None),
                                            book_format=book_format,
                                            index_in_lot=1,
                                            edition=edition)
                                print_obj(item, verbose)
                                item.save()

                            if "PREFACE" in fields:
                                collection = get_collection(collection)
                                if not collection.preface_and_paratexts:
                                    collection.preface_and_paratexts = fields.get("PREFACE")
                                else:
                                    collection.preface_and_paratexts = collection.preface_and_paratexts + " [...] " + \
                                                                      fields.get("PREFACE")
                                print_obj(collection, verbose)
                                collection.save()

                        # The following, including the try-except is meant to handle a dry run
                        if dry_run:
                            raise DryRunException()
            except DryRunException:
                print("Dry run finished without errors.")


