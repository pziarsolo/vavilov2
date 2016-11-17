from django.core.management.base import BaseCommand

from vavilov.db_management.base import load_initial_data


class Command(BaseCommand):
    help = 'load initial data into database'

    def handle(self, *args, **options):
        load_initial_data()
