from django.contrib.auth.models import User
from django.test import TestCase

from vavilov.db_management.tests import load_test_data
from vavilov.models import (Accession, AccessionRelationship, Cvterm, Assay,
                            Trait)


class AccessionTest(TestCase):

    def setUp(self):
        load_test_data()
        self.user = User.objects.get(username='user')

    def test_str(self):
        acc = Accession.objects.get(accession_number='BGV000932')
        assert str(acc) == 'Comav Gene bank(ESP026): BGV000932'

    def test_accession_dup_equi(self):
        is_duplicate = Cvterm.objects.get(cv__name='accession_relationship_types',
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

    def test_assays(self):
        assay = Assay.objects.get(name='NSF1')
        self.assertEqual(assay.get_absolute_url, '/assay/NSF1/')
        self.assertEqual(assay.props, {'campaign': 'NSF-March-2016'})
        self.assertEqual(assay.owner, self.user)
        self.assertEqual(len(assay.traits(user=self.user)), 1)

#         self.assertEqual(assay.plants(self.user).count(), 192)
#         self.assertEqual(assay.plants(self.admin).count(), 192)
#         self.assertEqual(assay.plants(self.user2).count(), 0)
#
#         self.assertEqual(assay.observations(self.user).count(), 13)
#         self.assertEqual(assay.observations(self.admin).count(), 13)
#         self.assertEqual(assay.observations(self.user2).count(), 0)

    def test_traits(self):
        trait = Trait.objects.get(name='Growth habit',
                                  assaytrait__assay__name='NSF1')
        self.assertEqual(trait.description, 'grow habit')


#         self.assertEqual(trait.observations(self.user).count(), 9)
#         self.assertEqual(trait.observations(self.admin).count(), 9)
#         self.assertEqual(trait.observations(self.user2).count(), 0)
