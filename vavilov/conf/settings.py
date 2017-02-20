from django.conf import settings
from pytz import timezone

# expose api rest to anyone
EXPOSE_API = getattr(settings, 'VAVILOV_EXPOSE_API', True)

# group that belongs public permissions
PUBLIC_GROUP_NAME = 'public'

# our timezone
OUR_TIMEZONE = timezone(settings.TIME_ZONE)

OBSERVATIONS_HAVE_TIME = getattr(settings, 'VAVILOV_OBSERVATIONS_HAVE_TIME',
                                 True)

# Whic logger use. We have two, vavilov.debug(console) and vavilov.prod(file).
APP_LOGGER = getattr(settings, 'VAVILOV_APP_LOGGER', 'vavilov.debug')

# When filtering observations, do by object
BY_OBJECT_OBS_PERM = getattr(settings, 'VAVILOV_BY_OBJECT_OBS_PERM', True)

# Max number of photos to show in gallery
MAX_PHOTO_IN_GALLERY = getattr(settings, 'VAVILOV_MAX_PHOTO_IN_GALLERY', 100)

# Key of the google map API-
GOOGLEMAPKEY = getattr(settings, 'VAVILOV_GOOGLEMAPKEY', None)

# Limit of observations in a search to convert to excel
MAX_OBS_TO_EXCEL = 1000

# Phenotype photos dir path
PHENO_PHOTO_DIR = getattr(settings, 'VAVILOV_PHENO_PHOTO_DIR', None)


DEFAULT_ACCESSION_SEARCH_FIELDS = ['accession', 'taxa', 'country', 'region',
                                   'biological_status', 'collecting_source']

ACCESSION_SEARCH_FIELDS = getattr(settings, 'VAVILOV_ACCESSION_SEARCH_FIELDS',
                                  DEFAULT_ACCESSION_SEARCH_FIELDS)

DEFAULT_ACCESSION_TABLE_FIELDS = ['accession_number', 'collecting_number',
                                  'organism', 'country', 'region',
                                  'province', 'local_name', 'collecting_date']

ACCESSION_TABLE_FIELDS = getattr(settings, 'VAVILOV_ACCESSION_TABLE_FIELDS',
                                 DEFAULT_ACCESSION_TABLE_FIELDS)

EXCLUDED_FIELDBOOK_TRAITS_TO_LOAD_IN_DB = ['Photos', 'Audio']
