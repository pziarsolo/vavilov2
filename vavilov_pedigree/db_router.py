from vavilov_pedigree import settings
from vavilov_pedigree.apps import VavilovPedigreeAppConfig


APP_NAME = VavilovPedigreeAppConfig.name
DB_NAME = settings.DB


class VavilovPedigreeRouter(object):
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label == APP_NAME:
            return DB_NAME
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        if model._meta.app_label == APP_NAME:
            return DB_NAME
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label == APP_NAME or \
           obj2._meta.app_label == APP_NAME:
            return True
        return None

    def allow_migrate(self, db, model):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        if db == DB_NAME:
            return model._meta.app_label == APP_NAME
        elif model._meta.app_label == APP_NAME:
            return False
        return None
