import argparse

from django.core.management.base import BaseCommand

from vavilov.conf.settings import EXCLUDED_FIELDBOOK_TRAITS_TO_LOAD_IN_DB
from vavilov.db_management.fieldbook import insert_newest_observations


class Command(BaseCommand):
    help = 'Export newst observations for the given plants\n'
    help += 'Create a fieldbook db file'

    def add_arguments(self, parser):
        parser.add_argument('outfhand', type=argparse.FileType('w'))
        parser.add_argument('-p', '--plants', required=True,
                            help='File with plant ids',
                            type=argparse.FileType('r'))
        parser.add_argument('-e', '--exclude', nargs='?',
                            default=EXCLUDED_FIELDBOOK_TRAITS_TO_LOAD_IN_DB,
                            help='Traits to be excluded from exportation')

    def handle(self, *args, **options):
        out_fhand = options['outfhand']
        plant_fhand = options['plants']
        excluded_traits = options['exclude']

        plants = [line.strip() for line in plant_fhand]

        insert_newest_observations(out_fhand, plants,
                                   excluded_traits=excluded_traits)
