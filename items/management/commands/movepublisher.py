from django.core.management.base import BaseCommand
from django.db import transaction

from items.models import PersonItemRelationRole, PersonItemRelation, Publisher

class Command(BaseCommand):
    help = 'Moves PersonItemRelations to Publisher.'

    default_role = "publisher"

    def add_arguments(self, parser):
        # Positional
        # ...

        # Optional
        parser.add_argument('--role-name', type=str,
                            help='Name of the PersonItemRelationRole (default: "{}")'.format(self.default_role))

        parser.add_argument('--dry-run', dest='dry-run', action='store_true',
                        help='Do not create Publisher objects and delete PersonItemRelations and PersonItemRelationRole objects')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Get the command line arguments
        role_name = kwargs['role-name'] if 'role-name' in kwargs else self.default_role
        dry_run = kwargs['dry-run']

        role = PersonItemRelationRole.objects.get(name=role_name)
        for personitemrelation in role.personitemrelation_set.all():
            publisher, created = Publisher.objects.get_or_create(publisher=personitemrelation.person,
                                                                edition=personitemrelation.item.edition)
            if created:
                print("Moved person {} ({}) to new Publisher {} ({}) for edition {} ({})".format(
                    personitemrelation.person,
                    personitemrelation.person_id,
                    publisher,
                    publisher.pk,
                    personitemrelation.item.edition,
                    personitemrelation.item.edition_id
                ))
            else:
                print("A Publisher with person {} ({}) and edition {} ({}) already exists.".format(
                    personitemrelation.person,
                    personitemrelation.person_id,
                    personitemrelation.item.edition,
                    personitemrelation.item.edition_id
                ))
        role.delete()  # also deletes it's personitemrelations

        if dry_run:
            transaction.set_rollback(True)

