from django.core.management.base import BaseCommand

from vavilov_pedigree.data_upload import (add_or_load_accessions,
                                          add_or_load_seedlot,
                                          add_or_load_plant_relationship,
                                          add_or_load_cross_experiments,
                                          add_or_load_plants)
from os.path import join


class Command(BaseCommand):
    help = 'load initial data into database'

    def add_arguments(self, parser):
        parser.add_argument('dir_fpath', help='directory with pedigree files')

    def handle(self, *args, **options):
        dirpath = options['dir_fpath']
        add_or_load_accessions(join(dirpath, 'varitome_passport.xlsx'))
        add_or_load_seedlot(join(dirpath, 'SeedLots_originals.xlsx'))
        add_or_load_plants(join(dirpath, 'NSF2_PA01_Sep_2016_plants.xlsx'))
        add_or_load_plants(join(dirpath, 'NSF2_CN0X_Feb_2016_plants.xlsx'))

        add_or_load_plant_relationship(join(dirpath, 'NSF2_PA01_Sep_2016_plant_clones.xlsx'))
        add_or_load_plant_relationship(join(dirpath, 'NSF2_CN0X_Feb_2016_plant_clones.xlsx'))

        add_or_load_cross_experiments(join(dirpath, 'cross_exps.xlsx'))
