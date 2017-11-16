import argparse

from django.core.management.base import BaseCommand

from vavilov.db_management.phenotype import (add_excel_observations,
                                             parse_qual_translator)


class Command(BaseCommand):
    help = 'Add observations from a excel file'

    def add_arguments(self, parser):
        parser.add_argument('infhand', type=argparse.FileType('rb'))
        parser.add_argument('-o', '--observer', required=False,
                            help='The user has made the observations')
        msg = 'If not in excel, The assay of the observations'
        parser.add_argument('-a', '--assay', required=False, help=msg)
        msg = 'If not in excel, Plant part associated with the observations'
        parser.add_argument('-p', '--plant_part', help=msg)

        parser.add_argument('-V', '--value_header', help='Value header name',
                            default='value')
        parser.add_argument('-d', '--creation_time_header',
                            default='creation_time',
                            help='Creation time header name')
        parser.add_argument('-A', '--assay_header', help='Assay header name',
                            default='assay')
        parser.add_argument('-s', '--observer_header', default='observer',
                            help='Observer header name')
        parser.add_argument('-t', '--trait_header', default='trait',
                            help='Trait header name')
        parser.add_argument('-c', '--accession_header', default='accession',
                            help='Accession header name')
        parser.add_argument('-r', '--plant_part_header', default='plant_part',
                            help='plant_part header name')
        parser.add_argument('-n', '--plant_number_header',
                            default='plant_number',
                            help='plant number header  name')
        parser.add_argument('-m', '--plant_name_header',
                            default='plant_name',
                            help='plant name header  name')
        parser.add_argument('--not-raise_on_error', action='store_false',
                            default=True)
        parser.add_argument('-g', '--view_perm_group',
                            help="group granting view perms")
        parser.add_argument('-u', '--obs_uid_header',
                            default='obs_uid',
                            help='Observation entity header name')
        parser.add_argument('--qualitative_translator',
                            type=argparse.FileType('rt'),
                            help='file with the qualitative translations')

    def handle(self, *args, **options):
        fhand = options['infhand']
        observer = options['observer']
        assay = options['assay']
        plant_part = options['plant_part']
        assay_header = options['assay_header']
        value_header = options['value_header']
        creation_time_header = options['creation_time_header']
        observer_header = options['observer_header']
        trait_header = options['trait_header']
        accession_header = options['accession_header']
        plant_part_header = options['plant_part_header']
        plant_number_header = options['plant_number_header']
        plant_name_header = options['plant_name_header']
        view_perm_gr = options['view_perm_group']
        obs_uid_header = options['obs_uid_header']
        raise_on_error = not options['not_raise_on_error']

        qual_trans_fhand = options['qualitative_translator']
        if qual_trans_fhand is not None:
            qual_translator = parse_qual_translator(qual_trans_fhand)
        else:
            qual_translator = None

        add_excel_observations(fhand.name, observer=observer,
                                       assay=assay, plant_part=plant_part,
                                       value_header=value_header,
                                       assay_header=assay_header,
                                       date_header=creation_time_header,
                                       observer_header=observer_header,
                                       trait_header=trait_header,
                                       accession_header=accession_header,
                                       plant_part_header=plant_part_header,
                                       plant_name_header=plant_name_header,
                                       plant_number_header=plant_number_header,
                                       view_perm_group=view_perm_gr,
                                       obs_uid_header=obs_uid_header,
                                       raise_on_error=raise_on_error,
                                       qualitative_translator=qual_translator)
