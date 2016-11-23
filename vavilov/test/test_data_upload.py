from os.path import join
from django.conf import settings as site_settings
from django.test import TestCase
from django.test.utils import override_settings

from vavilov.conf import settings
from vavilov.db_management.images import add_or_load_image_to_db
from vavilov.db_management.tests import load_test_data, TEST_DATA_DIR
from vavilov.models import (Cv, Cvterm, Accession, Person, Plant, Trait,
                            AssayTrait, Assay)


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
        inst = Person.objects.all().first()
        acc = Accession.objects.create(accession_number='VOYAGE',
                                       institute=inst)
        Plant.objects.create(accession=acc, plant_name='0F16NSF1CN06F04M179')
        trait_type = Cvterm.objects.get(cv__name='trait_types', name='image')
        trait = Trait.objects.create(name='image_leaf', type=trait_type)
        assay = Assay.objects.get(name='NSF1')
        AssayTrait.objects.create(trait=trait, assay=assay)

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
        assert obs_image.obs_entity.part.name == 'leaf'
