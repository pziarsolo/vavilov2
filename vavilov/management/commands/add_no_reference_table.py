import argparse
import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from vavilov.models import Cv, Db, Country


NO_REF_TABLES = {'cv': Cv, 'db': Db, 'country': Country}


class dialect(csv.excel):
    delimiter = ','
    skipinitialspace = True
    doublequote = True
    lineterminator = '\n'


class Command(BaseCommand):
    help = 'add Cv entryes in the database'

    def add_arguments(self, parser):
        parser.add_argument('infhand', type=argparse.FileType('r'))
        parser.add_argument('-t', '--table', type=str)

    def handle(self, *args, **options):
        fhand = options['infhand']
        table = options['table']
        model = NO_REF_TABLES[table]
        with transaction.atomic():
            for line in csv.DictReader(fhand, dialect=dialect):
                model.objects.get_or_create(**line)
