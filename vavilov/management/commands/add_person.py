import argparse

from django.core.management.base import BaseCommand

from vavilov.db_management.base import add_or_load_persons


class Command(BaseCommand):
    help = 'add Cvterm entries in the database'

    def add_arguments(self, parser):
        parser.add_argument('infhand', type=argparse.FileType('r'))

    def handle(self, *args, **options):
        fhand = options['infhand']
        add_or_load_persons(fhand)
