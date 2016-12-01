from django.apps import AppConfig
from django.conf import settings


class VavilovAppConfig(AppConfig):
    name = 'vavilov'

    def ready(self):
        if not settings.DEBUG:
            from vavilov.caches import get_passport_data_choices, get_taxons
            get_taxons()
            get_passport_data_choices()
