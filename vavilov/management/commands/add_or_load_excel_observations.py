import argparse

from django.core.management.base import BaseCommand

from vavilov.db_management.phenotype import add_or_load_excel_observations


class Command(BaseCommand):
    help = 'Add observations from a excel file'

    def add_arguments(self, parser):
        parser.add_argument('infhand', type=argparse.FileType('rb'))
        parser.add_argument('-o', '--observer', required=False,
                            help='The user has made the observations')
        parser.add_argument('-a', '--assay', required=True,
                            help='The assay of the observations')
        parser.add_argument('-V', '--value_header',
                            help='Value header name')
        parser.add_argument('-d', '--creation_time_header',
                            help='Creation time header name')
        parser.add_argument('-s', '--observer_header',
                            help='Observer header name')
        parser.add_argument('-t', '--trait_header',
                            help='Trait header name')
        parser.add_argument('-p', '--plant_part',
                            help='Plant part associated with the observations')

    def handle(self, *args, **options):
        fhand = options['infhand']
        observer = options['observer']
        assay = options['assay']
        value_header = options['value_header']
        creation_time_header = options['creation_time_header']
        observer_header = options['observer_header']
        trait_header = options['trait_header']
        plant_part = options['plant_part']

        add_or_load_excel_observations(fhand, observer=observer, assay=assay,
                                       value_header=value_header,
                                       date_header=creation_time_header,
                                       observer_header=observer_header,
                                       trait_header=trait_header,
                                       plant_part=plant_part)
