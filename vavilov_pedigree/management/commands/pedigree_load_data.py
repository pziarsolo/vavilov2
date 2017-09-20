from time import time
from django.core.management.base import BaseCommand

from vavilov_pedigree.data_upload import (add_or_load_accessions,
                                          add_or_load_seedlot,
                                          add_or_load_plant_relationship,
                                          add_or_load_cross_experiments,
                                          add_or_load_plants)
from os.path import join


def print_duration(msg, prev_time):
    now = time()
    print(msg + ': ' + str(round(now - prev_time, 2)))
    return now


class Command(BaseCommand):
    help = 'load initial data into database'

    def add_arguments(self, parser):
        parser.add_argument('dir_fpath', help='directory with pedigree files')

    def handle(self, *args, **options):
        dirpath = options['dir_fpath']
        prev_time = time()

        add_or_load_accessions(join(dirpath, 'varitome_passport.xlsx'))
        prev_time = print_duration('varitome_passport.xlsx', prev_time)

        add_or_load_seedlot(join(dirpath, 'SeedLots_originals.xlsx'))
        prev_time = print_duration('SeedLots_originals.xlsx', prev_time)

        add_or_load_plants(join(dirpath, 'NSF2_PA01_Sep_2016_plants.xlsx'))
        prev_time = print_duration('NSF2_PA01_Sep_2016_plants.xlsx', prev_time)

        add_or_load_plants(join(dirpath, 'NSF2_CN0X_Feb_2016_plants.xlsx'))
        prev_time = print_duration('NSF2_CN0X_Feb_2016_plants.xlsx', prev_time)

        add_or_load_plants(join(dirpath, 'NSF1_CN0X_Feb_2016_plants.xlsx'))
        prev_time = print_duration('NSF1_CN0X_Feb_2016_plants.xlsx', prev_time)

        add_or_load_plant_relationship(join(dirpath, 'NSF2_PA01_Sep_2016_plant_clones.xlsx'))
        prev_time = print_duration('NSF2_PA01_Sep_2016_plant_clones.xlsx', prev_time)

        add_or_load_plant_relationship(join(dirpath, 'NSF2_CN0X_Feb_2016_plant_clones.xlsx'))
        prev_time = print_duration('NSF2_CN0X_Feb_2016_plant_clones.xlsx', prev_time)

        add_or_load_cross_experiments(join(dirpath, 'Crosses_F16NSF2.xlsx'))
        prev_time = print_duration('Crosses_F16NSF2.xlsx', prev_time)

        add_or_load_cross_experiments(join(dirpath, 'Crosses_F16NSF3_upv.xlsx'))
        prev_time = print_duration('Crosses_F16NSF3_upv.xlsx', prev_time)

        # 2017 March
        dirpath_2017march = join(dirpath, 'SEP_2017')
        add_or_load_plants(join(dirpath_2017march, 'NSF2_PA01_March_2017_plants.xlsx'))
        prev_time = print_duration('NSF2_PA01_March_2017_plants.xlsx', prev_time)

        add_or_load_plants(join(dirpath_2017march, 'NSF3_AQ01_March_2017_plants.xlsx'))
        prev_time = print_duration('NSF3_AQ01_March_2017_plants.xlsx', prev_time)

        add_or_load_cross_experiments(join(dirpath_2017march, 'NSF2_PA01_March_2017_crosses.xlsx'))
        prev_time = print_duration('NSF2_PA01_March_2017_crosses.xlsx', prev_time)

        add_or_load_cross_experiments(join(dirpath_2017march, 'NSF3_AQ01_March_2017_crosses.xlsx'))
        prev_time = print_duration('NSF3_AQ01_March_2017_crosses.xlsx', prev_time)

        add_or_load_cross_experiments(join(dirpath_2017march, 'CRUCES_ESPECIFICOS-sep2017.xlsx'))
        prev_time = print_duration('CRUCES_ESPECIFICOS-sep2017.xlsx', prev_time)
