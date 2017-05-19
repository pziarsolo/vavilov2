
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test import TestCase
from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.test import APIClient as Client

from vavilov.db_management.base import add_location
from vavilov.db_management.tests import load_test_data
from vavilov.models import (Accession, Passport, Location, Cvterm,
                            AccessionRelationship)


# from django.test.client import Client
class AccessionViewTest(TestCase):
    def setUp(self):
        load_test_data()

    def test_list(self):
        client = Client()
        response = client.get(reverse('api:accession-list'))
        assert response.status_code == status.HTTP_200_OK

        client.login(username='admin', password='pass')
        response = client.get(reverse('api:accession-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 10
        assert 'accession_number' in response.data[0]
        assert b'BGV000933' in response.content

    def test_add_change_delete(self):
        client = Client()
        # add
        test_acc_number = 'prueba'
        response = client.post(reverse('api:accession-list'),
                               {'institute': 1, 'accession_number':
                                test_acc_number})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert client.login(username='admin', password='pass')
        response = client.post(reverse('api:accession-list'),
                               {'institute': 1, 'accession_number':
                                test_acc_number})
        assert response.status_code == status.HTTP_201_CREATED
        acc = Accession.objects.get(accession_number=test_acc_number)

        # change
        url = reverse('api:accession-detail', kwargs={'accession_number': acc.accession_number})
        response = client.put(url, {'accession_number': acc.accession_number,
                                    'institute': 2})
        assert response.status_code == status.HTTP_200_OK

        acc = Accession.objects.get(accession_number=test_acc_number)
        assert acc.institute.person_id == 2

        # delete
        response = client.delete(reverse('api:accession-detail',
                                         kwargs={'accession_number': acc.accession_number}))

        try:
            acc = Accession.objects.get(accession_number=test_acc_number)
            self.fail('does not exist expected')
        except Accession.DoesNotExist:
            pass

    def test_search(self):
        client = Client()
        acc = Accession.objects.get(accession_number='BGV000933')
        response = client.get(reverse('api:accession-list'),
                              {'accession': acc.accession_number})

        assert len(response.data) == 1
        assert response.data[0]['accession_number'] == acc.accession_number
        assert response.status_code == status.HTTP_200_OK

        # search by collecting code
        response = client.get(reverse('api:accession-list'),
                              {'accession': 'AN-L-18'})
        assert len(response.data) == 1
        assert response.data[0]['accession_number'] == 'BGV000917'
        assert response.status_code == status.HTTP_200_OK

        response = client.get(reverse('api:accession-list'),
                              {'accession': 'IVALSA',
                               'region': 'anda'})

        assert len(response.data) == 1


class PassportTest(TestCase):
    def setUp(self):
        load_test_data()

    def test_list(self):
        client = Client()
        response = client.get(reverse('api:passport-list'))
        assert response.status_code == status.HTTP_200_OK

        client.login(username='admin', password='pass')
        response = client.get(reverse('api:passport-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 8
        assert response.data[0]['local_name'] == 'Tomate de pera'

    def test_add_change_delete(self):
        client = Client()
        # add
        response = client.post(reverse('api:passport-list'),
                               {'accession': 1, 'local_name': 'tomate'})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert client.login(username='admin', password='pass')
        response = client.post(reverse('api:passport-list'),
                               {'accession': 1,
                                'local_name': 'tomate',
                                })
        assert response.status_code == status.HTTP_201_CREATED

        pass_id = Passport.objects.last().passport_id
        # change
        url = reverse('api:passport-detail', kwargs={'pk': pass_id})
        response = client.patch(url, {'local_name': 'tomate2'})
        assert response.status_code == status.HTTP_200_OK

        response = client.put(url, {'accession': 1, 'local_name': 'tomate'})
        assert response.status_code == status.HTTP_200_OK

        # delete
        response = client.delete(url)

        try:
            Passport.objects.get(passport_id=pass_id)
            self.fail('does not exist expected')
        except Passport.DoesNotExist:
            pass


class LocationTest(TestCase):
    def setUp(self):
        load_test_data()
        loc = add_location(region='aaa')
        new_group = Group.objects.create(name='test1')
        assign_perm('view_location', new_group, loc)

    def test_list(self):
        client = Client()
        response = client.get(reverse('api:location-list'))
        assert response.status_code == status.HTTP_200_OK

        assert len(response.data) == 5

        client.login(username='admin', password='pass')
        response = client.get(reverse('api:location-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 6
        assert response.data[-1]['region'] == 'aaa'

    def test_add_change_delete(self):
        client = Client()
        # add
        response = client.post(reverse('api:location-list'), {'region': 'reg1'})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert client.login(username='admin', password='pass')
        response = client.post(reverse('api:location-list'), {'region': 'reg1'})
        assert response.status_code == status.HTTP_201_CREATED

        loc_id = Location.objects.last().location_id
        # change
        url = reverse('api:location-detail', kwargs={'pk': loc_id})
        response = client.patch(url, {'region': 'reg2'})
        assert response.status_code == status.HTTP_200_OK

        url = reverse('api:location-detail', kwargs={'pk': loc_id})
        response = client.put(url, {'region': 'reg2'})
        assert response.status_code == status.HTTP_200_OK
        # delete
        response = client.delete(url)

        try:
            Location.objects.get(location_id=loc_id)
            self.fail('does not exist expected')
        except Location.DoesNotExist:
            pass


class AccessionRelTest(TestCase):
    def setUp(self):
        load_test_data()

    def test_list(self):
        client = Client()
        response = client.get(reverse('api:accessionrelationship-list'))

        assert response.status_code == status.HTTP_200_OK

        client.login(username='admin', password='pass')
        response = client.get(reverse('api:accessionrelationship-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_add_change_delete(self):
        client = Client()
        # add
        is_duplicated_from = Cvterm.objects.get(cv__name='relationship_types',
                                                name='is_duplicated_from')
        relation = {'object': 1, 'subject': 2,
                    'type': is_duplicated_from.cvterm_id}

        response = client.post(reverse('api:accessionrelationship-list'), relation)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert client.login(username='admin', password='pass')
        response = client.post(reverse('api:accessionrelationship-list'), relation)
        assert response.status_code == status.HTTP_201_CREATED

        acc_id = AccessionRelationship.objects.last().accession_relationship_id
        # change
        url = reverse('api:accessionrelationship-detail', kwargs={'pk': acc_id})
        response = client.patch(url, {'subject': 3})
        assert response.status_code == status.HTTP_200_OK

        url = reverse('api:accessionrelationship-detail', kwargs={'pk': acc_id})
        response = client.put(url, relation)

        assert response.status_code == status.HTTP_200_OK
        # delete
        response = client.delete(url)

        try:
            AccessionRelationship.objects.get(accession_relationship_id=acc_id)
            self.fail('does not exist expected')
        except AccessionRelationship.DoesNotExist:
            pass
