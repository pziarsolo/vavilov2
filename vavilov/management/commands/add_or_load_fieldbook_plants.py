import argparse

from django.core.management.base import BaseCommand

from vavilov.db_management.fieldbook import add_or_load_fieldbook_fields


class Command(BaseCommand):
    help = 'Add or load plants from fieldbook fields file'

    def add_arguments(self, parser):
        parser.add_argument('infhand', type=argparse.FileType('r'))
        parser.add_argument('-a', '--assay', required=True,
                            help='Assay where the traits are used')
        parser.add_argument('-p', '--plant_id_header', required=False,
                            default='unique_id',
                            help='Plant id header in the file')
        parser.add_argument('-i', '--accession',
                            help='Accession header name')
        parser.add_argument('-e', '--exp_field',
                            help='experimental field header name')
        parser.add_argument('-r', '--row',
                            help='Row header name')
        parser.add_argument('-c', '--column',
                            help='column header name')
        parser.add_argument('-n', '--pot_number',
                            help='Pot number header name')
        parser.add_argument('-s', '--synonym', nargs='?',
                            help='synonym header name')
        parser.add_argument('-d', '--seedlot', help='seedlot name')

    def handle(self, *args, **options):
        fhand = options['infhand']
        assay = options['assay']
        accession_header = options['accession']
        synonym_headers = options['synonym']
        if not isinstance(synonym_headers, list):
            synonym_headers = [synonym_headers]
        exp_fields_header = options['exp_field']
        row_header = options['row']
        column_header = options['column']
        pot_number_header = options['pot_number']
        plant_id_header = options['plant_id_header']
        seedlot_header = options['seedlot']

        add_or_load_fieldbook_fields(fhand.name, assay,
                                     accession_header=accession_header,
                                     plant_id_header=plant_id_header,
                                     synonym_headers=synonym_headers,
                                     experimental_field_header=exp_fields_header,
                                     row_header=row_header,
                                     column_header=column_header,
                                     pot_number_header=pot_number_header,
                                     seedlot_header=seedlot_header)
