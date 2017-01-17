import os

from django.conf import settings as site_settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand

from vavilov.conf.settings import PHENO_PHOTO_DIR
from vavilov.db_management.images import add_or_load_images


class Command(BaseCommand):
    help = '''It adds or loads observation images.

The images needs to have assay, plant and plant_part info in the exif's comments
The directory with the photos must be in MEDIA_ROOT and must be cofigured in settings
with PHENO_MANAGER_PHENE_PHOTOS
    The photos must be  inside dirs, better with accession names on it
    '''

    def add_arguments(self, parser):
        parser.add_argument('-g', '--view-perm-group',
                            help='Group to grand view permissions')
        parser.add_argument('-c', '--create_plant', action='store_true',
                            help='Create plants or look for them in db')
        parser.add_argument('-s', '--use_image_id_as_plant_id',
                            action='store_true',
                            help='If no plant id use image id as plant id')

    def handle(self, *args, **options):
        view_perm_group = options['view_perm_group']
        create_plant = options['create_plant']
        use_image_id_as_plant_id = options['use_image_id_as_plant_id']

        pheno_photo_dirname = PHENO_PHOTO_DIR
        if pheno_photo_dirname is None:
            msg = 'PHENO_MANAGER_PHENO_PHOTOS is not configured'
            raise ImproperlyConfigured(msg)

        pheno_photo_dir = os.path.join(site_settings.MEDIA_ROOT,
                                       PHENO_PHOTO_DIR)
        add_or_load_images(pheno_photo_dir, view_perm_group=view_perm_group,
                           create_plant=create_plant,
                           use_image_id_as_plant_id=use_image_id_as_plant_id)
