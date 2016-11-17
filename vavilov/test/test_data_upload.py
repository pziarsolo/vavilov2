from django.test import TestCase

from vavilov.db_management.tests import load_test_data
from vavilov.models import (Cv, Cvterm, Accession)


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
