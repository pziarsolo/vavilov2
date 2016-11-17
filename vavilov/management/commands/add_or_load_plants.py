import argparse

from django.core.management.base import BaseCommand

from vavilov.db_management.phenotype import add_or_load_plants


class Command(BaseCommand):
    help = 'add Cv entries in the database'

    def add_arguments(self, parser):
        parser.add_argument('infhand', type=argparse.FileType('r'))
        parser.add_argument('-a', '--assay')

    def handle(self, *args, **options):
        fhand = options['infhand']
        assay = options['assay']
        add_or_load_plants(fhand.name, assay)
