import argparse

from django.core.management.base import BaseCommand

from vavilov.conf.settings import EXCLUDED_FIELDBOOK_TRAITS_TO_LOAD_IN_DB
from vavilov.db_management.fieldbook import add_or_load_fielbook_observations


class Command(BaseCommand):
    help = 'Add observations from a fieldbook database'

    def add_arguments(self, parser):
        parser.add_argument('infhand', type=argparse.FileType('r'))
        parser.add_argument('-a', '--assay', required=True, nargs='*')
        parser.add_argument('-o', '--observer', required=True)
        parser.add_argument('-e', '--excluded', nargs='*',
                            help='exclude traits to load in db',
                            default=EXCLUDED_FIELDBOOK_TRAITS_TO_LOAD_IN_DB)

    def handle(self, *args, **options):
        fhand = options['infhand']
        observer = options['observer']
        assays = options['assay']
        excluded_traits = options['excluded']
        add_or_load_fielbook_observations(fhand.name, observer, assays,
                                          excluded_traits=excluded_traits)
