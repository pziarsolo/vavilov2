from django.core.management.base import BaseCommand

from vavilov.db_management.tests import load_test_data


class Command(BaseCommand):
    help = 'load initial data into database'

    def handle(self, *args, **options):
        load_test_data()
