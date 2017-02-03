import argparse

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from vavilov.utils.streams import create_excel_from_queryset
from vavilov.views.observation import filter_observations
from vavilov.views.tables import ObservationsTable


class Command(BaseCommand):
    help = 'Load Initial data'

    def add_arguments(self, parser):
        parser.add_argument('-o', '--out_file', type=argparse.FileType('w'))
        parser.add_argument('-a', '--accession', help='accesion')
        parser.add_argument('-p', '--plant', help='Plant_name')
        parser.add_argument('-r', '--plant_part', help='Plant part')
        parser.add_argument('-s', '--assay', help='Assay')
        parser.add_argument('-t', '--traits', help='traits, separated by commas')

    def handle(self, *args, **options):
        out_fhand = options['out_file']
        user = User.objects.get(username='admin')
        search_criteria = {}
        if options['accession']:
            search_criteria['accession'] = options['accession']
        if options['plant']:
            search_criteria['plant'] = options['plant']
        if options['plant_part']:
            search_criteria['plant_part'] = options['plant_part']
        if options['assay']:
            search_criteria['assay'] = options['assay']
        if options['traits']:
            search_criteria['traits'] = options['traits']

        queryset = filter_observations(search_criteria, user)[0]
        create_excel_from_queryset(out_fhand.name, queryset, ObservationsTable)
