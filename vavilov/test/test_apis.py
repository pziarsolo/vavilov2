import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from vavilov.db_management.tests import load_test_data


class ApiTest(TestCase):
    def setUp(self):
        load_test_data()

    def test_accession_number(self):
        client = Client()
        response = client.get(reverse('api_accession_numbers'))
        accession_numbers = json.loads(response.content.decode())
        assert len(accession_numbers) == 13

    def test_taxons(self):
        client = Client()
        response = client.get(reverse('api_taxons'))
        taxons = json.loads(response.content.decode())
        assert len(taxons) == 14

        url = reverse('api_taxons') + "?term=br"
        response = client.get(url)
        taxons = json.loads(response.content.decode())
        taxons = [t['label'] for t in taxons]
        assert taxons == ['Brassica', 'Brassica oleracea',
                          'Brassica oleracea acephala']
