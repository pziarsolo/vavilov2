from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient as Client
from rest_framework.reverse import reverse
from rest_framework import status


class AuthTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin',
                                                   email='p@p.es',
                                                   password='pass')
        self.admintoken = Token.objects.create(user=self.admin)

    def test_token_auth(self):
        client = Client()
        response = client.post('/api-token-auth/', {'username': 'admin',
                                                    'password': 'pass'})
        self.assertEqual(response.data['token'], self.admintoken.key)

        response = client.get(reverse('api:user-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        client.credentials(HTTP_AUTHORIZATION='Token ' + self.admintoken.key)
        response = client.get(reverse('api:user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
