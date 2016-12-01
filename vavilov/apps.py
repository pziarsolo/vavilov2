from django.apps import AppConfig
from django.conf import settings
from django.db.models import signals


class VavilovAppConfig(AppConfig):
    name = 'vavilov'

    def ready(self):
        if not settings.DEBUG:
            from vavilov.caches import get_passport_data_choices, get_taxons
            from vavilov.models import AccessionTaxa, Passport

            get_taxons()
            get_passport_data_choices()

            signals.post_save.connect(receiver=get_taxons,
                                      sender=AccessionTaxa)
            signals.post_save.connect(receiver=get_passport_data_choices,
                                      sender=Passport)
