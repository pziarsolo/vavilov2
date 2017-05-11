from os.path import join
from django.conf import settings as site_settings
from django.test import TestCase
from django.test.utils import override_settings

from vavilov.conf import settings
from vavilov.db_management.images import add_or_load_image_to_db
from vavilov.db_management.tests import load_test_data, TEST_DATA_DIR
from vavilov.models import Cv, Cvterm, Accession, Observation, \
    ObservationRelationship
from vavilov.db_management.phenotype import (add_or_load_excel_related_observations,
                                             add_or_load_excel_traits,
                                             parse_qual_translator)
from django.core.management import execute_from_command_line

TRAITS2_FPATH = join(TEST_DATA_DIR, 'traits2.xlsx')
QUAL_TRASLATOR_FPATH = join(TEST_DATA_DIR, 'qualitative_translator.csv')


class FixturesTest(TestCase):

    def setUp(self):
        load_test_data()

    def test_initial(self):
        'It loads the fixtures.'
        assert Cv.objects.all()
        assert Cvterm.objects.all()

    def test_add_accessions(self):
        Accession.objects.get(accession_number='BGV000917')
        Accession.objects.get(accession_number='BGV000933')
        acc = Accession.objects.get(accession_number='BGV000934')
        assert acc.passport.location.country


class ImageTests(TestCase):
    def setUp(self):
        load_test_data()
#         inst = Person.objects.all().first()
#         acc = Accession.objects.create(accession_number='VOYAGE',
#                                        institute=inst)
        # Plant.objects.create(accession=acc, plant_name='0F16NSF1CN06F04M179')
#         trait_type = Cvterm.objects.get(cv__name='trait_types', name='image')
#         trait = Trait.objects.create(name='image_leaf', type=trait_type)
#         assay = Assay.objects.get(name='NSF1')
#         AssayTrait.objects.create(trait=trait, assay=assay)

    @override_settings()
    def test_image_load(self):
        image_fname = '0F16NSF1CN06F04M179_leaf_s36iba69.jpg'
        unchanged_settings = site_settings.MEDIA_ROOT
        with self.settings(MEDIA_ROOT=join(TEST_DATA_DIR, 'media/')):
            image_fpath = join(site_settings.MEDIA_ROOT,
                               settings.PHENO_PHOTO_DIR,
                               'VOYAGE', 'leaf', image_fname)

            obs_image = add_or_load_image_to_db(image_fpath)
            obs_image2 = add_or_load_image_to_db(image_fpath)
            assert obs_image == obs_image2
            image = obs_image.image
            thumb = obs_image.thumbnail

            # Can not test real behavioru. looks like global settings are
            # cached and does not take into account the change I do in tests
            assert image.path == join(unchanged_settings,
                                      settings.PHENO_PHOTO_DIR,
                                      'VOYAGE', 'leaf', image_fname)
            assert thumb.path == join(unchanged_settings,
                                      settings.PHENO_PHOTO_DIR,
                                      'VOYAGE', 'leaf', 'thumbnails',
                                      image_fname)
            assert image.url == join(site_settings.MEDIA_URL,
                                     settings.PHENO_PHOTO_DIR,
                                     'VOYAGE', 'leaf', image_fname)

            assert thumb.url == join(site_settings.MEDIA_URL,
                                     settings.PHENO_PHOTO_DIR,
                                     'VOYAGE', 'leaf', 'thumbnails',
                                     image_fname)
        assert obs_image.observation.obs_entity.part.name == 'leaf'


class RelatedObservationsTest(TestCase):
        def setUp(self):
            load_test_data()
            add_or_load_excel_traits(TRAITS2_FPATH, assays=['NSF1'])

        def test_related_observations_leaf(self):
            qual_translator = parse_qual_translator(open(QUAL_TRASLATOR_FPATH))
            assert Observation.objects.count() == 15
            assert not ObservationRelationship.objects.count()
            related_obs_fpath = join(TEST_DATA_DIR, 'obs_related_leaf.xlsx')
            add_or_load_excel_related_observations(related_obs_fpath,
                                                   qual_translator=qual_translator)
            assert Observation.objects.count() == 43
            assert ObservationRelationship.objects.count() == 28

            add_or_load_excel_related_observations(related_obs_fpath,
                                                   qual_translator=qual_translator)
            assert Observation.objects.count() == 43
            assert ObservationRelationship.objects.count() == 28

        def test_related_obs_fruits(self):
            assert Observation.objects.count() == 15
            related_obs_fpath = join(TEST_DATA_DIR, 'obs_related_fruits.xlsx')
            add_or_load_excel_related_observations(related_obs_fpath)
            assert Observation.objects.count() == 187

            add_or_load_excel_related_observations(related_obs_fpath)
            assert Observation.objects.count() == 187

        def test_related_obs_color(self):
            assert Observation.objects.count() == 15

            related_obs_fpath = join(TEST_DATA_DIR, 'obs_related_color.xlsx')
            add_or_load_excel_related_observations(related_obs_fpath,
                                                   one_part_per_plant=True)
            assert Observation.objects.count() == 57
            add_or_load_excel_related_observations(related_obs_fpath,
                                                   one_part_per_plant=True)
            assert Observation.objects.count() == 57

        def test_binary(self):
            related_obs_fpath = join(TEST_DATA_DIR, 'obs_related_leaf.xlsx')
            execute_from_command_line(['manage.py',
                                       'add_or_load_excel_related_observations',
                                       related_obs_fpath,
                                       '--qualitative_translator',
                                       QUAL_TRASLATOR_FPATH])
