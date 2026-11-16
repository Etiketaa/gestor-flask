from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Organization, Role, User


class AuthApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org = Organization.objects.create(name='Test Org', slug='test-org')
        self.role = Role.objects.create(name='admin', organization=self.org)
        self.user = User.objects.create_user(
            username='apiuser', password='pass123',
            organization=self.org, role=self.role, status='approved',
        )

    def test_register_organization(self):
        url = reverse('register-organization')
        data = {
            'organization_name': 'Nueva Org',
            'organization_slug': 'nueva-org',
            'username': 'nuevo',
            'password': 'pass123',
        }
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertIn('access', resp.data['tokens'])
        self.assertIn('refresh', resp.data['tokens'])

    def test_login_returns_jwt_tokens(self):
        url = reverse('login')
        data = {
            'username': 'apiuser',
            'password': 'pass123',
            'organization_slug': 'test-org',
        }
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access', resp.data['tokens'])
        self.assertIn('refresh', resp.data['tokens'])
        self.assertEqual(resp.data['user']['username'], 'apiuser')

    def test_login_wrong_password(self):
        url = reverse('login')
        data = {
            'username': 'apiuser',
            'password': 'mal',
            'organization_slug': 'test-org',
        }
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_me_requires_auth(self):
        url = reverse('me')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 401)

    def test_me_with_token(self):
        url = reverse('me')
        resp = self.client.post(reverse('login'), {
            'username': 'apiuser', 'password': 'pass123',
            'organization_slug': 'test-org',
        }, format='json')
        token = resp.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['user']['username'], 'apiuser')
