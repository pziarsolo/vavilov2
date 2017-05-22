from django.apps import AppConfig


class VavilovAppConfig(AppConfig):
    name = 'vavilov'

    def ready(self):
        import vavilov.signals
