from os.path import join, dirname
import sys
from django.db.utils import IntegrityError

from vavilov.db_management.excel import excel_dict_reader, get_sheet_names
import vavilov_pedigree
from vavilov_pedigree.models import (Accession, SeedLot, Plant, Assay,
                                     CrossExperiment, CrossExperimentSeedLot,
                                     PlantRelationship, CrossPlant, FATHER,
                                     MOTHER)
from vavilov.api.views import accession

TEST_DATA_DIR = join(dirname(vavilov_pedigree.__file__), 'test', 'data')


def add_or_load_accessions(fpath):
    for row in excel_dict_reader(fpath):
        accession = row['CODE']
        collecting_number = row['COLLECTING CODE']
        if accession:
            Accession.objects.get_or_create(accession_number=accession,
                                            collecting_number=collecting_number)


def add_or_load_seedlot(fpath):
    for row in excel_dict_reader(fpath):
        accession = row['Accession']
        seed_lot = row['SeedLot']
        description = row['Description']
        seeds_weight = row['SeedsWeight']
        if accession and seed_lot:
            accession = Accession.objects.get_or_create(accession_number=accession)[0]
            SeedLot.objects.get_or_create(accession=accession, name=seed_lot,
                                          description=description,
                                          seeds_weight=seeds_weight)


def add_or_create_plant(plant_name, seedlot_name, glasshouse=None,
                        row_num=None, pot_number=None):
    if plant_name and seedlot_name:
        seed_lot = SeedLot.objects.get(name=seedlot_name)
        try:
            Plant.objects.get_or_create(seed_lot=seed_lot,
                                        plant_name=plant_name,
                                        experimental_field=glasshouse,
                                        row=row_num, pot_number=pot_number)
        except IntegrityError:
            print(plant_name)
            raise


def add_or_load_plants(fpath):
    for row in excel_dict_reader(fpath):
        plant_name = row['PlantName']
        seedlot_name = row['SeedLot']
        glasshouse = row.get('glasshouse', None)
        row_num = row.get('row', None)
        pot_number = row.get('pot_number', None)
        add_or_create_plant(plant_name, seedlot_name, glasshouse, row_num,
                            pot_number)


def add_or_load_plant_relationship(fpath):
    for row in excel_dict_reader(fpath):
        plant_name1 = row['Plant1']
        plant_name2 = row['Plant2']
        plant1 = Plant.objects.get(plant_name=plant_name1)
        plant2 = Plant.objects.get(plant_name=plant_name2)
        PlantRelationship.objects.get_or_create(subject=plant1,
                                                object=plant2)


def add_or_load_cross(father_accession, mother_accession, father_plant,
                      mother_plant, offspring, offspring_fruit, assay_name,
                      offspring_accession, offspring_description,
                      offspring_location):

    cross_exp_desc = '{}x{}'.format(mother_accession, father_accession)

    same_name_exps = CrossExperiment.objects.filter(description__icontains=cross_exp_desc).order_by('description')
    if same_name_exps:
        last_number = int(same_name_exps.last().description.split('-')[-1])
    else:
        last_number = 0

    cross_exp_desc += '-{}'.format(last_number + 1)

    if (father_plant and mother_plant and offspring and assay_name and
            cross_exp_desc):
        try:
            father_plant = Plant.objects.get(plant_name=father_plant)
        except Plant.DoesNotExist:
            print(father_plant + ' does not exist')
            continue
        except Plant.MultipleObjectsReturned:
            print(father_plant + ' multiple times')
            raise
        try:
            mother_plant = Plant.objects.get(plant_name=mother_plant)
        except Plant.DoesNotExist:
            print(mother_plant + ' does not exist')
            continue

        # plant/accession codes must match
        error = False
        if father_plant.seed_lot.accession.accession_number != father_accession:
            msg = '{} and {} not match'.format(father_accession, father_plant.plant_name)
            print(msg + ' father')
            error = True

        if mother_plant.seed_lot.accession.accession_number != mother_accession:
            msg = '{} and {} not match'.format(mother_accession, mother_plant.plant_name)
            print(msg + ' mother')
            error = True
        if error:
            continue

        assay = Assay.objects.get_or_create(name=assay_name)[0]
        try:
            cross_exp, created = CrossExperiment.objects.get_or_create(description=cross_exp_desc,
                                                                       assay=assay)
        except IntegrityError:
            print(cross_exp_desc)
            raise
        if created:
            CrossPlant.objects.get_or_create(cross=cross_exp, plant=father_plant,
                                             type=FATHER)
            for father_clones in father_plant.clones:
                CrossPlant.objects.get_or_create(cross=cross_exp,
                                                 plant=father_clones,
                                                 type=FATHER)

            CrossPlant.objects.get_or_create(cross=cross_exp,
                                             plant=mother_plant,
                                             type=MOTHER)
            for mother_clones in mother_plant.clones:
                CrossPlant.objects.get_or_create(cross=cross_exp,
                                                 plant=mother_clones,
                                                 type=MOTHER)
        # seed:
        if offspring_accession:
            accession = Accession.objects.get_or_create(accession_number=offspring_accession)[0]
        else:
            accession = None
        try:
            offspring = SeedLot.objects.get_or_create(name=offspring,
                                                      accession=accession,
                                                      description=offspring_description,
                                                      fruit=offspring_fruit,
                                                      location=offspring_location)[0]
        except IntegrityError:
            print(offspring)
            raise

        CrossExperimentSeedLot.objects.get_or_create(cross_experiment=cross_exp,
                                                     seed_lot=offspring)


def add_or_load_cross_experiments(fpath):
    for row in excel_dict_reader(fpath):
        father_accession = row['Father(Accession)']
        mother_accession = row['Mother(Accession)']
        father_plant = row['Father(plant)']
        mother_plant = row['Mother(plant)']
        offspring = row['Offspring(seedlot)']
        offspring_fruit = row['Fruit #']
        assay_name = row['Assay']
        offspring_accession = row['OffspringAccession']
        offspring_description = row['OffspringDescription']
        add_or_load_cross(father_accession, mother_accession, father_plant,
                          mother_plant, offspring, offspring_fruit, assay_name,
                          offspring_accession, offspring_description)


def _check_row(seedlot, accession_number, col_number):
    errors = []

    try:
        Accession.objects.get(accession_number=accession_number,
                              collecting_number=col_number)
    except Accession.DoesNotExist:
        errors.append('Accession {} and collecting code {} does not fit'.format(accession_number,
                                                                                col_number))
    try:
        SeedLot.objects.get(name=seedlot, accession__accession_number=accession_number)
    except SeedLot.DoesNotExist:
        errors.append('Seedlot {} dowes not match with accession: {}'.format(seedlot,
                                                                             accession_number))
    return errors


def check_data_integrity(data):
    fail = False
    for index, row in enumerate(data):
        row_number = index + 1

        father_seedlot = row['Father seedlot']
        father_accession = row['Father (Accesion)']
        father_col_code = row['test p']
        fa_errors = _check_row(father_seedlot, father_accession, father_col_code)

        mother_seedlot = row['Mother seedlot']
        mother_accession = row['Mother (Accession)']
        mother_col_code = row['test m']
        mo_errors = _check_row(mother_seedlot, mother_accession, mother_col_code)

        if fa_errors:
            fail = True
            for error in fa_errors:
                sys.stderr.write('Row {} Father: {}\n'.format(row_number, error))
        if mo_errors:
            fail = True
            for error in mo_errors:
                sys.stderr.write('Row {} Mother: {}\n'.format(row_number, error))
    return fail


def add_or_load_crosses_data(fpath):
    sheet_names = get_sheet_names(fpath)
    for sheet_name in sheet_names:
        sheet_data = list(excel_dict_reader(fpath, sheet_name=sheet_name))
        fail = check_data_integrity(sheet_data)
        if fail:
            sys.exit(1)

        # add_plants
        for row in sheet_data:
            father_seedlot = row['Father seedlot']
            father_plant = row['Father (plant)']
            add_or_create_plant(father_plant, father_seedlot)

            mother_seedlot = row['Mother seedlot']
            mother_plant = row['Mother (plant)']

            add_or_create_plant(mother_plant, mother_seedlot)

        # add crosses
        for row in sheet_data:
            father_accession = row['Father(Accession)']
            mother_accession = row['Mother(Accession)']
            father_plant = row['Father(plant)']
            mother_plant = row['Mother(plant)']
            offspring = row['Offspring(seedlot)']
            offspring_fruit = row['Fruit #']
            offspring_location = row.get('Location', None)
            assay_name = row['Assay']
            offspring_accession = row['OffspringAccession']
            offspring_description = row['OffspringDescription']
            add_or_load_cross(father_accession, mother_accession, father_plant,
                              mother_plant, offspring, offspring_fruit, assay_name,
                              offspring_accession, offspring_description, offspring_location)


def load_test_data():
    add_or_load_accessions(join(TEST_DATA_DIR, 'accessions.xlsx'))
    add_or_load_seedlot(join(TEST_DATA_DIR, 'seed_lots.xlsx'))
    add_or_load_plants(join(TEST_DATA_DIR, 'plants.xlsx'))
    add_or_load_plant_relationship(join(TEST_DATA_DIR, 'plant_clones.xlsx'))
    add_or_load_cross_experiments(join(TEST_DATA_DIR, 'cross_exps.xlsx'))
