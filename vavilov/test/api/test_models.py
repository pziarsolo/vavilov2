from django.test import TestCase

from vavilov.db_management.tests import load_test_data
from vavilov.models import Accession, AccessionRelationship, Cvterm


class AccessionTest(TestCase):

    def setUp(self):
        load_test_data()

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
