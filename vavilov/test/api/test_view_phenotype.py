from os.path import join, dirname

from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.test import TestCase
from guardian.shortcuts import remove_perm
from rest_framework import status
from rest_framework.test import APIClient as Client

import vavilov
from vavilov.db_management.tests import load_test_data
from vavilov.models import Assay, Plant, Cvterm, AssayProp
from vavilov.db_management.fieldbook import (add_or_load_fieldbook_fields,
                                             add_or_load_fieldbook_traits,
                                             add_or_load_fielbook_observations)

TEST_DATA_DIR = join(dirname(vavilov.__file__), 'test', 'data')
NSF1_PLANTS = join(TEST_DATA_DIR, 'fieldbook_field.csv')
NSF1_TRAITS = join(TEST_DATA_DIR, 'fieldbook_traits.trt')
OBSERVATIONS_FPATH = join(TEST_DATA_DIR, 'fieldbook.db')


class AssayViewTest(TestCase):
    def setUp(self):
        load_test_data()

    def test_list(self):
        client = Client()
        response = client.get(reverse('api:assay-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

        assert client.login(username='admin', password='pass')
        response = client.get(reverse('api:assay-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        assert 'name' in response.data[0]

        # list only users assays
        assert client.login(username='user', password='pass')
        response = client.get(reverse('api:assay-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def xtest_check_perm(self):
        client = Client()
        user = User.objects.get(username='user')
        assert client.login(username='user', password='pass')
        url = reverse('api:assay-detail', kwargs={'name': 'NSF1'})
        response = client.get(url)
        props1 = response.data['props']
        print('with_perm', props1)

        assayprop = AssayProp.objects.get(assay_prop_id=1)
        remove_perm('view_assayprop', user, assayprop)
        response = client.get(url)
        props2 = response.data['props']
        print('without_perm', props2)

        assert props1 != props2

    def test_add_change_delete(self):
        client = Client()
        # add
        test_assayname = 'prueba'
        response = client.post(reverse('api:assay-list'), {'name': test_assayname})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert client.login(username='admin', password='pass')
        user = User.objects.get(username='user')
        user_url = reverse('api:user-detail', kwargs={'username': user.username})
        response = client.post(reverse('api:assay-list'), {'name': test_assayname,
                                                           'owner': user_url})
        assert response.status_code == status.HTTP_201_CREATED

        # change
        url = reverse('api:assay-detail', kwargs={'name': test_assayname})
        response = client.put(url, {'name': test_assayname, 'owner': user_url,
                                    'description': 'description'})
        assert response.status_code == status.HTTP_200_OK

        assay = Assay.objects.get(name=test_assayname)
        assert assay.description == 'description'

        # delete
        response = client.delete(url)

        try:
            Assay.objects.get(name=test_assayname)
            self.fail('does not exist expected')
        except Assay.DoesNotExist:
            pass

    def test_search(self):
        client = Client()
        assay = Assay.objects.get(name='NSF1')
        response = client.get(reverse('api:assay-list'), {'name': assay.name})
        assert not response.data

        assert client.login(username='user', password='pass')
        response = client.get(reverse('api:assay-list'), {'name': assay.name})
        assert len(response.data) == 1

        assert response.data[0]['name'] == assay.name
        assert response.status_code == status.HTTP_200_OK


class PlantViewTest(TestCase):
    def setUp(self):
        load_test_data()

    def test_list(self):
        user = User.objects.get(username='user')
        nsf3 = Assay.objects.get(name='NSF3')
        assert not user.has_perm('vavilov.view_assay', nsf3)

        nsf1 = Assay.objects.get(name='NSF1')
        assert user.has_perm('vavilov.view_assay', nsf1)

        client = Client()
        response = client.get(reverse('api:plant-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

        assert client.login(username='admin', password='pass')
        response = client.get(reverse('api:plant-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 19
        # print(response.data[0]['assays'][0])
        # assert response.data[0]['assays'][0] == 'http://testserver/assays/1/'
        assert 'plant_id' in response.data[0]

        # list only users assays
        assert client.login(username='user', password='pass')

    def test_add_change_delete(self):
        client = Client()
        # add
        test_plantname = 'prueba'
        response = client.post(reverse('api:plant-list'), {'plant_name': test_plantname})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert client.login(username='admin', password='pass')
        response = client.post(reverse('api:plant-list'), {'plant_name': test_plantname,
                                                           'accession': 1})
        assert response.status_code == status.HTTP_201_CREATED

        # change
        url = reverse('api:plant-detail', kwargs={'plant_name': test_plantname})
        response = client.patch(url, {'plant_name': test_plantname,
                                      'row': '1'})
        assert response.status_code == status.HTTP_200_OK

        plant = Plant.objects.get(plant_name=test_plantname)
        assert plant.row == '1'

        # delete
        response = client.delete(url)

        try:
            Plant.objects.get(plant_name=test_plantname)
            self.fail('does not exist expected')
        except Plant.DoesNotExist:
            pass

    def test_search(self):
        client = Client()
        plant = Plant.objects.get(plant_name='BGV000917_plant')
        response = client.get(reverse('api:plant-list'),
                              {'plant_name': plant.plant_name})
        assert not response.data

        assert client.login(username='admin', password='pass')
        response = client.get(reverse('api:plant-list'),
                              {'plant_name': plant.plant_name})
        assert len(response.data) == 2
        assert response.data[0]['plant_name'] == plant.plant_name
        assert response.status_code == status.HTTP_200_OK


class AssayPlantViewTest(TestCase):
    def setUp(self):
        load_test_data()

    def test_list(self):
        client = Client()
        response = client.get(reverse('api:assayplant-list'))
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        response = client.get(reverse('api:assayplant-detail', kwargs={'pk': 1}))
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_destroy(self):
        client = Client()
        response = client.delete(reverse('api:assayplant-detail', kwargs={'pk': 1}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert client.login(username='user', password='pass')
        response = client.delete(reverse('api:assayplant-detail', kwargs={'pk': 1}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert client.login(username='admin', password='pass')
        response = client.delete(reverse('api:assayplant-detail', kwargs={'pk': 1}))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def create(self):
        client = Client()
        response = client.get(reverse('api:assayplant-list'), {'assay': 2,
                                                               'plant': 1})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert client.login(username='admin', password='pass')
        response = client.get(reverse('api:assayplant-list'), {'assay': 2,
                                                               'plant': 1})
        assert response.status_code == status.HTTP_201_CREATED


class AssayPropViewTest(TestCase):
    def setUp(self):
        load_test_data()

    def test_list(self):
        client = Client()
        response = client.get(reverse('api:assayprop-list'))
        assert response.content == b'[]'
        assert response.status_code == status.HTTP_200_OK

        assert client.login(username='admin', password='pass')
        response = client.get(reverse('api:assayprop-list'))
        response = client.get(reverse('api:assayprop-detail', kwargs={'pk': 1}))

        assert response.status_code == status.HTTP_200_OK
        assert 'value' in response.data and 'type' in response.data

    def test_create_mod_delete(self):
        client = Client()
        cvterm = Cvterm.objects.filter(cv__name='assay_props').last()
        response = client.post(reverse('api:assayprop-list'), {'assay': 1,
                                                               'type': cvterm.cvterm_id,
                                                               'value': '11'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert client.login(username='admin', password='pass')

        response = client.post(reverse('api:assayprop-list'), {'assay': 1,
                                                               'type': cvterm.cvterm_id,
                                                               'value': '11'})
        assert response.status_code == status.HTTP_201_CREATED

        url = reverse('api:assayprop-detail',
                      kwargs={'pk': response.data['assay_prop_id']})
        response = client.patch(url, {'value': '12'})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['value'] == '12'


class FieldbookObservationTest(TestCase):
    def setUp(self):
        load_test_data()
        self.user = User.objects.get(username='user')
        Assay.objects.create(name='assay1', owner=self.user)
        Group.objects.create(name='assay1')
        add_or_load_fieldbook_fields(NSF1_PLANTS, 'assay1',
                                     accession_header='BGV',
                                     synonym_headers=['Accession'])
        add_or_load_fieldbook_traits(NSF1_TRAITS, assays=['assay1'])

        add_or_load_fielbook_observations(OBSERVATIONS_FPATH, 'test',
                                          ['assay1'])

    def test_list(self):
        client = Client()
        response = client.get(reverse('api:fieldbook_observation-list'))
        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert client.login(username='admin', password='pass')
        response = client.get(reverse('api:fieldbook_observation-list'))
        assert len(response.data) == 8

    def test_create(self):
        client = Client()
        assert client.login(username='admin', password='pass')
        response = client.post(reverse('api:fieldbook_observation-list'),
                               {'name': 'aa'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {'detail': 'Incorrect input data'}

        fieldbook_obs = {'rid': '0F16NSF1CN02F01M001', 'parent': 'Area2',
                         'userValue': '23', 'person': 'test',
                         'timeTaken': '2017-05-25 14:56:08+0200'}
        response = client.post(reverse('api:fieldbook_observation-list'),
                               fieldbook_obs)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['rid'] == fieldbook_obs['rid']

        response = client.post(reverse('api:fieldbook_observation-list'),
                               fieldbook_obs)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'detail': 'Already in db'}


# class PlantPartViewTest(TestCase):
#     def setUp(self):
#         load_test_data()
#
#     def test_list(self):
#         client = Client()
#         response = client.get(reverse('plantpart-list'))
