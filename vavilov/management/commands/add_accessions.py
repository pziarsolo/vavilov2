import argparse

from django.core.management.base import BaseCommand

from vavilov.cache_management import update_caches
from vavilov.db_management.base import add_accessions


class Command(BaseCommand):
    help = 'add Cv entries in the database'

    def add_arguments(self, parser):
        parser.add_argument('infhand', type=argparse.FileType('r'))
        parser.add_argument('-s', '--silent', action='store_true')

    def handle(self, *args, **options):
        fhand = options['infhand']
        silent = options['silent']
        add_accessions(fhand, silent)
        update_caches()
