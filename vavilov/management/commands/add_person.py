import argparse
import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from vavilov.db_management.base import comma_dialect
from vavilov.models import Cv, Cvterm, Person


class Command(BaseCommand):
    help = 'add Cvterm entries in the database'

    def add_arguments(self, parser):
        parser.add_argument('infhand', type=argparse.FileType('r'))

    def handle(self, *args, **options):
        fhand = options['infhand']
        with transaction.atomic():
            for entry in csv.DictReader(fhand, dialect=comma_dialect):
                cv = Cv.objects.get(name='person_types')
                type_ = Cvterm.objects.get(cv=cv, name=entry['type'])
                Person.objects.get_or_create(name=entry['name'],
                                             description=entry['description'],
                                             type=type_)
