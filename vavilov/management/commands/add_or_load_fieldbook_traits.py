import argparse

from django.core.management.base import BaseCommand

from vavilov.db_management.fieldbook import add_or_load_fieldbook_traits


class Command(BaseCommand):
    help = 'Add or load traits from fieldbook traits file'

    def add_arguments(self, parser):
        parser.add_argument('infhand', type=argparse.FileType('r'))
        parser.add_argument('-a', '--assay', required=True, nargs='+',
                            help='Assay where the traits are used')

    def handle(self, *args, **options):
        fhand = options['infhand']
        assays = options['assay']
        add_or_load_fieldbook_traits(fhand.name, assays)
