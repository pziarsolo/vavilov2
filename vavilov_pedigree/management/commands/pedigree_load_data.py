from django.core.management.base import BaseCommand

from vavilov_pedigree.data_upload import load_data


class Command(BaseCommand):
    help = 'load initial data into database'

    def add_arguments(self, parser):
        parser.add_argument('dir_fpath', help='directory with pedigree files')

    def handle(self, *args, **options):
        dir_fpath = options['dir_fpath']
        load_data(dir_fpath)
