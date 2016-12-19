from django.conf import settings
from pytz import timezone

# expose api rest to anyone
EXPOSE_API = getattr(settings, 'VAVILOV_EXPOSE_API', True)

# group that belongs public permissions
PUBLIC_GROUP_NAME = 'public'

# our timezone
OUR_TIMEZONE = timezone(settings.TIME_ZONE)


DB_CODE_PREFIX = getattr(settings, 'VAVILOV_DB_CODE_PREFIX', None)
if DB_CODE_PREFIX is None:
    raise ValueError('DB_CODE_PREFIX needs to be set for the database')

GENEBANK_CODE = getattr(settings, 'VAVILOV_GENEBANK_CODE', None)
if GENEBANK_CODE is None:
    raise RuntimeError('settings.VAVILOV_GENEBANK_CODE must be setted in projects configuration')


DEF_ACCESSION_SEARCH_FORM_FIELDS = ['accession', 'taxa', 'country', 'region',
                                    'biological_status', 'collecting_source']

ACCESSION_SEARCH_FORM_FIELDS = getattr(settings,
                                       'VAVILOV_ACCESSION_FORM_FIELDS',
                                       DEF_ACCESSION_SEARCH_FORM_FIELDS)

DEF_ACCESSION_SEARCH_RESULT_FIELDS = ['accession_number', 'collecting_number',
                                      'organism', 'country', 'region',
                                      'province', 'local_name',
                                      'collecting_date']

ACCESSION_SEARCH_RESULT_FIELDS = getattr(settings,
                                         'VAVILOV_ACCESSION_SEARCH_RESULT_FIELDS',
                                         DEF_ACCESSION_SEARCH_RESULT_FIELDS)

# TAXONS_CACHE_FILE = os.path.join(settings.CACHE_DIR, 'taxons.json')
# SEARCH_CHOICES_CACHE_FILE = os.path.join(settings.CACHE_DIR, 'search_choices.json')

# Phenotype data
PHENO_PHOTO_DIR = getattr(settings, 'VAVILOV_PHENO_PHOTO_DIR', None)

EXCLUDED_FIELDBOOK_TRAITS_TO_LOAD_IN_DB = ['Photos', 'Audio']
