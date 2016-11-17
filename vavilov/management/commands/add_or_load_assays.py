import argparse

from django.core.management.base import BaseCommand

from vavilov.db_management.phenotype import add_or_load_assays


class Command(BaseCommand):
    help = 'Add or load assays'

    def add_arguments(self, parser):
        parser.add_argument('infhand', type=argparse.FileType('r'))

    def handle(self, *args, **options):
        fhand = options['infhand']
        add_or_load_assays(fhand.name)
