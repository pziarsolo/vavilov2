from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient as Client

from vavilov.db_management.tests import load_test_data
from vavilov.models import Cvterm


class UserViewTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin',
                                                   email='p@p.es',
                                                   password='pass')

    def test_list(self):
        client = Client()
        response = client.get(reverse('user-list'))
        assert response.status_code == status.HTTP_403_FORBIDDEN

        client.login(username='admin', password='pass')
        response = client.get(reverse('user-list'))
        assert response.status_code == status.HTTP_200_OK

    def test_add_change_delete(self):
        client = Client()
        client.login(username='admin', password='pass')

        response = client.post(reverse('user-list'), {'username': 'test',
                                                      'email': 'p2@p.es',
                                                      'password': 'pass'})

        assert response.status_code == status.HTTP_201_CREATED
        user = User.objects.get(username='test')
        new_email = 'p3@p.es'
        response = client.patch(reverse('user-detail', kwargs={'username': user.username}),
                                {'email': new_email})
        assert response.status_code == status.HTTP_200_OK
        user = User.objects.get(username='test')
        assert user.email == new_email
        client.logout()

        client.login(username='test', password='pass')
        # user can see itself
        response = client.get(reverse('user-detail', kwargs={'username': user.username}))
        assert response.status_code == status.HTTP_200_OK

        # user can change password
        url = reverse('user-set-password', kwargs={'username': user.username})
        response = client.post(url, {'password': 'pass2'})
        assert response.status_code == 200

        # user can not destroy its user
        response = client.delete(reverse('user-detail', kwargs={'username': user.username}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # any user can not see user list
        response = client.get(reverse('user-list'))
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # user can not create other user
        response = client.post(reverse('user-list'), {'username': 'test2',
                                                      'email': 'p4@p.es',
                                                      'password': 'pass'})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        client.logout()

        #
        client.login(username='admin', password='pass')
        # admin can change password
        url = reverse('user-set-password', kwargs={'username': user.username})
        response = client.post(url, {'password': 'pass3'})
        assert response.status_code == status.HTTP_200_OK

        url = reverse('user-detail', kwargs={'username': user.username})
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT


class GroupViewTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin',
                                                   email='p@p.es',
                                                   password='pass')
        self.user = User.objects.create_user(username='user',
                                             email='p@p.es',
                                             password='pass')

    def test_list(self):
        client = Client()
        response = client.get(reverse('group-list'))
        assert response.status_code == status.HTTP_403_FORBIDDEN

        client.login(username='admin', password='pass')
        response = client.get(reverse('group-list'))
        assert response.status_code == status.HTTP_200_OK

    def test_create_mod_delete(self):
        client = Client()
        response = client.post(reverse('group-list'), {'name': 'group1'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        client.login(username='admin', password='pass')
        response = client.post(reverse('group-list'), {'name': 'group1'})
        assert response.status_code == status.HTTP_201_CREATED

        response = client.put(reverse('group-detail', kwargs={'name': 'group1'}),
                              {'name': 'group1_dup'})
        assert response.status_code == status.HTTP_200_OK

        response = client.delete(reverse('group-detail', kwargs={'name': 'group1_dup'}))
        assert response.status_code == status.HTTP_204_NO_CONTENT


class DbViewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin',
                                                   email='p@p.es',
                                                   password='pass')
        self.user = User.objects.create_user(username='user',
                                             email='p@2p.es',
                                             password='pass')

    def test_list(self):
        client = Client()
        response = client.get(reverse('db-list'))
        assert response.status_code == status.HTTP_200_OK

        client.login(username='admin', password='pass')
        response = client.get(reverse('db-list'))
        assert response.status_code == status.HTTP_200_OK

    def test_add_mod_delete(self):
        client = Client()
        response = client.post(reverse('db-list'), {'name': 'test',
                                                    'description': 'fakedb'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert client.login(username='admin', password='pass')
        response = client.post(reverse('db-list'), {'name': 'test',
                                                    'description': 'fakedb'})
        assert response.status_code == status.HTTP_201_CREATED

        response = client.patch(reverse('db-detail', kwargs={'pk': 1}),
                                {'description': 'fakedb2'})
        assert response.status_code == status.HTTP_200_OK

        client.logout()
        response = client.patch(reverse('db-detail', kwargs={'pk': 1}),
                                {'description': 'fakedb2'})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response = client.delete(reverse('db-detail', kwargs={'pk': 1}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert client.login(username='admin', password='pass')
        response = client.get(reverse('db-detail', kwargs={'pk': 1}),
                              {'description': 'fakedb2'})
        assert response.data['description'] == 'fakedb2'

        response = client.delete(reverse('db-detail', kwargs={'pk': 1}))
        assert response.status_code == status.HTTP_204_NO_CONTENT


class CVViewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin',
                                                   email='p@p.es',
                                                   password='pass')
        self.user = User.objects.create_user(username='user',
                                             email='p@2p.es',
                                             password='pass')

    def test_list(self):
        client = Client()
        response = client.get(reverse('cv-list'))
        assert response.status_code == status.HTTP_200_OK

        client.login(username='admin', password='pass')
        response = client.get(reverse('cv-list'))
        assert response.status_code == status.HTTP_200_OK

    def test_add_mod_delete(self):
        client = Client()
        response = client.post(reverse('cv-list'), {'name': 'test',
                                                    'description': 'fakedb'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert client.login(username='admin', password='pass')
        response = client.post(reverse('cv-list'), {'name': 'test',
                                                    'description': 'fakedb'})
        assert response.status_code == status.HTTP_201_CREATED

        response = client.patch(reverse('cv-detail', kwargs={'name': 'test'}),
                                {'description': 'fakedb2'})
        assert response.status_code == status.HTTP_200_OK

        client.logout()
        response = client.patch(reverse('cv-detail', kwargs={'name': 'test'}),
                                {'description': 'fakedb2'})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response = client.delete(reverse('cv-detail', kwargs={'name': 'test'}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert client.login(username='admin', password='pass')
        response = client.get(reverse('cv-detail', kwargs={'name': 'test'}),
                              {'description': 'fakedb2'})
        assert response.data['description'] == 'fakedb2'

        response = client.delete(reverse('cv-detail', kwargs={'name': 'test'}))
        assert response.status_code == status.HTTP_204_NO_CONTENT


class CvtermViewTests(TestCase):
    def setUp(self):
        load_test_data()

    def test_list(self):
        client = Client()
        url = reverse('cvterm-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        client.login(username='admin', password='pass')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_add_mod_delete(self):
        client = Client()
        response = client.post(reverse('cvterm-list'), {'cv': 'http://testserver/api/cvs/biological_status/',
                                                        'name': 'test'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert client.login(username='admin', password='pass')
        response = client.post(reverse('cvterm-list'), {'cv': 'http://testserver/api/cvs/biological_status/',
                                                        'name': 'test'})
        assert response.status_code == status.HTTP_201_CREATED
        cvterm = Cvterm.objects.get(cv__name='biological_status', name='test')

        response = client.patch(reverse('cvterm-detail',
                                        kwargs={'pk': cvterm.cvterm_id}),
                                {'name': 'fakedb2'})
        assert response.status_code == status.HTTP_200_OK

        client.logout()
        response = client.patch(reverse('cvterm-detail',
                                        kwargs={'pk': cvterm.cvterm_id}),
                                {'name': 'fakedb2'})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response = client.delete(reverse('cvterm-detail',
                                         kwargs={'pk': cvterm.cvterm_id}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert client.login(username='admin', password='pass')
        response = client.get(reverse('cvterm-detail',
                                      kwargs={'pk': cvterm.cvterm_id}))
        assert response.data['name'] == 'fakedb2'

        response = client.delete(reverse('cvterm-detail',
                                         kwargs={'pk': cvterm.cvterm_id}))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_search(self):
        client = Client()
        response = client.get(reverse('cvterm-list'))
        assert len(response.data) > 64

        response = client.get(reverse('cvterm-list'), {'cv': 'biological_status'})
        assert len(response.data) == 21


class CountryViewTests(TestCase):
    def setUp(self):
        load_test_data()

    def test_view(self):
        client = Client()
        response = client.get(reverse('country-list'))
        assert response.status_code == status.HTTP_200_OK

        assert client.login(username='admin', password='pass')
        response = client.get(reverse('country-list'))
        assert response.status_code == status.HTTP_200_OK

        client.logout()
        response = client.get(reverse('country-detail', kwargs={'pk': 1}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'UNKNOWNCOUNTRYORIGIN'

    def test_add_mod_delete(self):
        client = Client()
        assert client.login(username='admin', password='pass')
        response = client.delete(reverse('country-detail', kwargs={'pk': 1}))
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        response = client.patch(reverse('country-detail', kwargs={'pk': 1}))
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        response = client.put(reverse('country-detail', kwargs={'pk': 1}))
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_search(self):
        client = Client()
        response = client.get(reverse('country-list'), {'name': 'spain'})
        assert len(response.data) == 1

        response = client.get(reverse('country-list'), {'name': 's'})
        assert len(response.data) == 102

        response = client.get(reverse('country-list'))
        assert len(response.data) == 250


class PersonViewTests(TestCase):
    def setUp(self):
        load_test_data()

    def test_view(self):
        client = Client()
        response = client.get(reverse('person-list'))
        assert response.status_code == status.HTTP_200_OK

        assert client.login(username='admin', password='pass')
        response = client.get(reverse('person-list'))
        assert response.status_code == status.HTTP_200_OK

        client.logout()
        response = client.get(reverse('person-detail', kwargs={'name': 'ESP026'}))
        assert response.status_code == status.HTTP_200_OK

# TODO, person tests, taxa tests
