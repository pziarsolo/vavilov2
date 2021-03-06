from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from vavilov.db_management.tests import load_test_data
from vavilov.models import Accession


class AccessionViewTest(TestCase):
    def setUp(self):
        load_test_data()

    def test_simple(self):
        client = Client()
        response = client.get(reverse('accession-detail',
                                      kwargs={'accession_number': 'BGV000933'}))
        assert response.status_code == 200

        assert b'BGV000933' in response.content

    def test_search(self):
        client = Client()
        response = client.get(reverse('accession-list'))
        assert response.status_code == 200

        acc = Accession.objects.get(accession_number='BGV000933')
        response = client.post(reverse('accession-list'),
                               {'accession': acc.accession_number})

        assert response.status_code == 302
        assert reverse('accession-detail', kwargs={'accession_number': 'BGV000933'}) in response.url

        response = client.post(reverse('accession-list'),
                               {'accession': 'BGV00093'})
        assert response.status_code == 200
        assert response.context['table'].as_values()[1][0] == 'BGV000932'

        # search by collecting code
        response = client.post(reverse('accession-list'),
                               {'accession': 'AN-L-18'})

        assert response.status_code == 302
        assert reverse('accession-detail', kwargs={'accession_number': 'BGV000917'}) in response.url


class ObservationsViewTest(TestCase):
    def setUp(self):
        load_test_data()

    def test_observations(self):
        client = Client()
        response = client.get(reverse('observation-list'))
        assert response.status_code == 200

        response = client.post(reverse('observation-list'),
                               {'accession': 'BGV000'})
        assert response.status_code == 200
        assert response.context['object_list'] is None

        assert client.login(username='user', password='pass')
        response = client.post(reverse('observation-list'),
                               {'accession': 'BGV000'})
        assert response.status_code == 200
        assert response.context['table'].as_values()
