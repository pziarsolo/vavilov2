from django.test import TestCase
from vavilov_pedigree.data_upload import load_test_data
from vavilov_pedigree.models import Plant, CrossExperiment, Accession, SeedLot, \
    Assay


class FixturesTest(TestCase):

    def setUp(self):
        load_test_data()

    def test_initial(self):
        assert Plant.objects.all()


class ModelTest(TestCase):
    def setUp(self):
        load_test_data()

    def test_cross_exp(self):
        cross_exp = CrossExperiment.objects.get(description='selot1xselot2')
        offsprings = cross_exp.offspring
        assert offsprings.count() == 2
        assert offsprings[0].name == 'newseed2'

    def test_accession(self):
        acc = Accession.objects.get(accession_number='acc1')
        assert acc.seed_lots.count() == 3

    def test_seed_lot(self):
        seed_lot = SeedLot.objects.first()
        assert seed_lot.description == 'desc1'
        assert seed_lot.fathers is None
        seed_lot = SeedLot.objects.last()
        assert seed_lot.fathers
        assert seed_lot.description is None
        assert seed_lot.fathers.count() == 3
        assert seed_lot.mothers.count() == 3


    def test_assay(self):
        assert Assay.objects.first().cross_experiments.count() == 3

    def test_plant(self):
        plant3 = Plant.objects.get(plant_name='plant3')
        assert len(plant3.clones) == 2
        plant1 = Plant.objects.get(plant_name='plant1')
        assert len(plant1.clones) == 2
        plant7 = Plant.objects.get(plant_name='plant7')
        assert not plant7.clones
        plant3 = Plant.objects.get(plant_name='plant3')
        assert len(plant3.clones) == 2
