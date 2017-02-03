from os.path import join, dirname

from vavilov.db_management.excel import excel_dict_reader

import vavilov_pedigree
from vavilov_pedigree.models import (Accession, SeedLot, Plant, Assay,
                                     CrossExperiment, CrossExperimentSeedLot,
                                     PlantRelationship, CrossPlant, FATHER,
    MOTHER)
from collections import Counter


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


def add_or_load_plants(fpath):
    for row in excel_dict_reader(fpath):
        plant_name = row['PlantName']
        seedlot_name = row['SeedLot']
        glasshouse = row.get('glasshouse', None)
        row_num = row.get('row', None)
        pot_number = row.get('pot_number', None)

        if plant_name and seedlot_name:
            seed_lot = SeedLot.objects.get(name=seedlot_name)
            Plant.objects.get_or_create(seed_lot=seed_lot,
                                        plant_name=plant_name,
                                        experimental_field=glasshouse,
                                        row=row_num, pot_number=pot_number)


def add_or_load_plant_relationship(fpath):
    for row in excel_dict_reader(fpath):
        plant_name1 = row['Plant1']
        plant_name2 = row['Plant2']
        plant1 = Plant.objects.get(plant_name=plant_name1)
        plant2 = Plant.objects.get(plant_name=plant_name2)
        PlantRelationship.objects.get_or_create(subject=plant1,
                                                object=plant2)


def add_or_load_cross_experiments(fpath):
    counter = Counter()
    for row in excel_dict_reader(fpath):

        father_accession = row['Father(Accession)']
        mother_accession = row['Mother(Accession)']
        replica = row['replicate']
        father_plant = row['Father(plant)']
        mother_plant = row['Mother(plant)']
        offspring = row['Offspring(seedlot)']
        offspring_fruit = row['Fruit #']
        assay_name = row['Assay']

        cross_exp_desc = '{}x{}'.format(mother_accession, father_accession)
        counter[cross_exp_desc] += 1
        cross_exp_desc += '-{}'.format(counter[cross_exp_desc])

        offspring_accession = row['OffspringAccession']
        offspring_description = row['OffspringDescription']


        if father_plant and mother_plant and offspring and assay_name and cross_exp_desc:

            father_plant = Plant.objects.get_or_create(plant_name=father_plant)[0]
            mother_plant = Plant.objects.get_or_create(plant_name=mother_plant)[0]

            # plant/accession codes must match
            assert father_plant.seed_lot.accession.accession_number == father_accession
            assert mother_plant.seed_lot.accession.accession_number == mother_accession


            assay = Assay.objects.get_or_create(name=assay_name)[0]
            cross_exp, created = CrossExperiment.objects.get_or_create(description=cross_exp_desc,
                                                                       assay=assay)
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
            offspring = SeedLot.objects.get_or_create(name=offspring,
                                                      accession=accession,
                                                      description=offspring_description,
                                                      fruit=offspring_fruit)[0]

            CrossExperimentSeedLot.objects.get_or_create(cross_experiment=cross_exp,
                                                         seed_lot=offspring)


def load_data(dirpath):
    add_or_load_accessions(join(dirpath, 'accessions.xlsx'))
    add_or_load_seedlot(join(dirpath, 'seed_lots.xlsx'))
    add_or_load_plants(join(dirpath, 'plants.xlsx'))
    add_or_load_plant_relationship(join(dirpath, 'plant_clones.xlsx'))
    add_or_load_cross_experiments(join(dirpath, 'cross_exps.xlsx'))



def load_test_data():
    load_data(TEST_DATA_DIR)
