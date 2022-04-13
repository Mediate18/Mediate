import csv
from django.core.management.base import BaseCommand
from items.models import PersonItemRelation


class Command(BaseCommand):
    help = 'Puts PersonItemRelations, Persons and Items in CSV files'

    default_role = "publisher"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('relations_csv_file', type=str)
        parser.add_argument('persons_csv_file', type=str)
        parser.add_argument('items_csv_file', type=str)

    def handle(self, *args, **kwargs):
        with open(kwargs['relations_csv_file'], 'w', newline='') as relations_csv_file,\
             open(kwargs['persons_csv_file'], 'w', newline='') as persons_csv_file,\
             open(kwargs['items_csv_file'], 'w', newline='') as items_csv_file:
            
            relations_writer = csv.writer(relations_csv_file)
            relations_writer.writerow(['ID', 'Person ID', 'Item ID', 'Role'])
            
            persons_writer = csv.writer(persons_csv_file)
            persons_writer.writerow(['ID', 'Short nme', 'Surname', 'First names', 'Date of birth', 'Date of death',
                                     'Sex', 'City of birth', 'City of death'])
            
            items_writer = csv.writer(items_csv_file)
            items_writer.writerow(['ID', 'Short title', 'Catalogue', 'Book format', 'Edition', 'Language'])
            
            persons_seen = set()
            items_seen = set()

            relations = PersonItemRelation.objects.all()
            for relation in relations:
                relations_writer.writerow([
                    str(relation.uuid),
                    str(relation.person_id),
                    str(relation.item_id),
                    relation.role
                ])

                person = relation.person
                if str(person.uuid) not in persons_seen:
                    persons_seen.add(str(person.uuid))
                    persons_writer.writerow([
                        str(person.uuid),
                        person.short_name,
                        person.surname,
                        person.first_names,
                        person.date_of_birth,
                        person.date_of_death,
                        person.sex,
                        person.city_of_birth,
                        person.city_of_death
                    ])

                item = relation.item
                if str(item.uuid) not in items_seen:
                    items_seen.add(str(item.uuid))
                    items_writer.writerow([
                        str(item.uuid),
                        item.short_title,
                        item.lot.collection,
                        item.book_format,
                        item.edition,
                        ", ".join([lang.language.name for lang in item.languages.all()])
                    ])
