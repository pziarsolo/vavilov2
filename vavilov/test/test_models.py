from django.contrib.auth.models import User
from django.test import TestCase

from vavilov.db_management.tests import load_test_data
from vavilov.models import (Accession, AccessionRelationship, Cvterm, Assay,
                            Trait, Plant, ObservationEntity, Observation)


class AccessionTest(TestCase):

    def setUp(self):
        load_test_data()
        self.user = User.objects.get(username='user')
        self.user2 = User.objects.get(username='user2')
        self.admin = User.objects.get(username='admin')

    def test_str(self):
        acc = Accession.objects.get(accession_number='BGV000932')
        assert str(acc) == 'Comav Gene bank(ESP026): BGV000932'

    def test_accession_dup_equi(self):
        is_duplicate = Cvterm.objects.get(cv__name='relationship_types',
                                          name='is_a_duplicated')
        acc = Accession.objects.get(accession_number='BGV000932')
        dup_rel_numbers = AccessionRelationship.objects.filter(subject=acc, type=is_duplicate)
        dup_numbers = [dup_rel.object for dup_rel in dup_rel_numbers]

        assert len(dup_numbers) == 1
        assert dup_numbers[0].accession_number == 'IVALSA 38'

        assert len(acc.duplicated_accessions_and_equivalents) == 1
        assert acc.duplicated_accessions_and_equivalents[0].accession_number == 'IVALSA 38'

    def test_accession_collecting(self):
        assert not Accession.objects.get(accession_number='BGV000934').collecting_accession
        acc = Accession.objects.get(accession_number='BGV000932')
        assert acc.collecting_accession == ('ESP026', 'AN-L-33')

    def test_donor_accession(self):
        acc = Accession.objects.get(accession_number='BGV000928')
        assert acc.donor_accession.accession_number == 'IVALSA 37'

    def test_passpor_data(self):
        acc = Accession.objects.get(accession_number='BGV000932')
        assert acc.passport

        acc = Accession.objects.get(accession_number='IVALSA 38')
        assert not acc.passport

    def test_organism(self):
        acc = Accession.objects.get(accession_number='BGV000928')
        assert acc.organism == 'Capsicum annuum , Variety annuum'

        acc = Accession.objects.get(accession_number='BGV000932')
        assert acc.organism == 'Capsicum annuum'

        acc = Accession.objects.get(accession_number='BGV000933')
        assert acc.organism == 'Capsicum spp'

    def test_assay(self):
        acc = Accession.objects.get(accession_number='BGV000928')
        assert acc.assays(self.user)[0].name == 'NSF1'

    def test_plants(self):
        acc = Accession.objects.get(accession_number='BGV000928')
        plant = acc.plants(self.user)[0]
        assert plant.plant_name == 'BGV000928_plant'

    def test_observations(self):
        acc = Accession.objects.get(accession_number='BGV000928')
        assert acc.observations(self.user).count() == 6
        assert acc.observations(self.user2).count() == 0


class PhenotypeTest(TestCase):
    def setUp(self):
        load_test_data()
        self.user = User.objects.get(username='user')
        self.user2 = User.objects.get(username='user2')
        self.admin = User.objects.get(username='admin')

    def test_assays(self):
        assay = Assay.objects.get(name='NSF1')
        self.assertEqual(assay.get_absolute_url(), '/assay/NSF1/')
        self.assertEqual(assay.props, {'campaign': 'NSF-March-2016'})
        self.assertEqual(assay.owner, self.user)
        self.assertEqual(len(assay.traits(user=self.user)), 3)
        self.assertEqual(assay.plants(self.user).count(), 18)
        self.assertEqual(assay.plants(self.admin).count(), 18)
        self.assertEqual(assay.plants(self.user2).count(), 0)

        self.assertEqual(assay.observations(self.user).count(), 13)
        self.assertEqual(assay.observations(self.admin).count(), 13)
        self.assertEqual(assay.observations(self.user2).count(), 0)

    def test_traits(self):
        trait = Trait.objects.get(name='Growth habit',
                                  assaytrait__assay__name='NSF1')
        self.assertEqual(trait.description, 'grow habit')

        trait = Trait.objects.get(name='Area', assaytrait__assay__name='NSF1')
        self.assertEqual(trait.observations(self.user).count(), 12)
        self.assertEqual(trait.observations(self.admin).count(), 12)
        self.assertEqual(trait.observations(self.user2).count(), 0)

    def test_plants(self):
        plants = Plant.objects.all()
        plant = plants.first()
        self.assertEqual(plant.assays(self.user)[0].name, 'NSF1')
        self.assertEqual(plant.assays(self.user2)[0].name, 'NSF3')
        plant = Plant.objects.get(plant_name='BGV000917_NSF1_2')
        assert plant.observations(self.user).count() == 2

    def test_obs_entity(self):
        obs_entitys = ObservationEntity.objects.all()
        obs_entity = obs_entitys.first()
        assert str(obs_entity.accession) == "Comav Gene bank(ESP026): BGV000917"

        self.assertEqual(obs_entity.plants(self.user).count(), 1)
        self.assertEqual(obs_entity.observations(self.user).count(), 1)

    def test_observations(self):
        obs = Observation.objects.all().first()
        assert str(obs.accession) == "Comav Gene bank(ESP026): BGV000917"
