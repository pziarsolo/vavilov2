import argparse

from django.core.management.base import BaseCommand

from vavilov.db_management.phenotype import (parse_qual_translator,
                                             add_or_load_excel_related_observations,
                                             PHOTO_HEADER, ASSAY_HEADER,
                                             PLANT_HEADER, PLANT_PART_HEADER,
                                             ACCESSION_HEADER)


class Command(BaseCommand):
    help = 'Add observations from a excel file'

    def add_arguments(self, parser):
        parser.add_argument('infhand', type=argparse.FileType('rb'))
        parser.add_argument('-A', '--assay_header', help='Assay header name',
                            default=ASSAY_HEADER)
        parser.add_argument('-m', '--plant_name_header', default=PLANT_HEADER,
                            help='plant name header  name')
        parser.add_argument('-r', '--plant_part_header', default=PLANT_PART_HEADER,
                            help='plant_part header name')
        parser.add_argument('-c', '--accession_header', default=ACCESSION_HEADER,
                            help='Accession header name')
        parser.add_argument('-p', '--photo_id_header', default=PHOTO_HEADER,
                            help='photo_id header name')
#         parser.add_argument('--not-raise_on_error', action='store_false',
#                             default=True)
        parser.add_argument('-g', '--view_perm_group',
                            help="group granting view perms")
        parser.add_argument('--qualitative_translator',
                            type=argparse.FileType('rt'),
                            help='file with the qualitative translations')

        parser.add_argument('--one_part_per_plant', action='store_true',
                            default=False)

    def handle(self, *args, **options):
        fhand = options['infhand']
        assay_header = options['assay_header']
        accession_header = options['accession_header']
        plant_part_header = options['plant_part_header']
        plant_name_header = options['plant_name_header']
        photo_header = options['photo_id_header']
        view_perm_gr = options['view_perm_group']
        # raise_on_error = not options['not_raise_on_error']
        qual_trans_fhand = options['qualitative_translator']
        one_part_per_plant = options['one_part_per_plant']

        if qual_trans_fhand is not None:
            qual_translator = parse_qual_translator(qual_trans_fhand)
        else:
            qual_translator = None

        add_or_load_excel_related_observations(fhand.name, assay_header=assay_header,
                                               plant_header=plant_name_header,
                                               plant_part_header=plant_part_header,
                                               accession_header=accession_header,
                                               photo_header=photo_header,
                                               perm_gr=view_perm_gr,
                                               one_part_per_plant=one_part_per_plant,
                                               qual_translator=qual_translator)
