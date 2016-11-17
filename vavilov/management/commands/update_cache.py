from django.core.management.base import BaseCommand
from vavilov.cache_management import update_caches


class Command(BaseCommand):
    help = 'update cache files'

    def handle(self, *args, **options):
        update_caches()
