from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Organization, Role, User

User = get_user_model()


class OrganizationModelTest(TestCase):
    def test_crear_organizacion(self):
        org = Organization.objects.create(
            name='Ferretería Test', slug='ferreteria-test'
        )
        self.assertEqual(org.name, 'Ferretería Test')
        self.assertEqual(org.slug, 'ferreteria-test')
        self.assertIsNotNone(org.created_at)


class RoleModelTest(TestCase):
    def test_crear_rol(self):
        org = Organization.objects.create(name='Org', slug='org')
        role = Role.objects.create(name='admin', organization=org)
        self.assertEqual(role.name, 'admin')
        self.assertEqual(role.organization, org)


class UserModelTest(TestCase):
    def test_crear_usuario(self):
        org = Organization.objects.create(name='Org', slug='org')
        role = Role.objects.create(name='admin', organization=org)
        user = User.objects.create_user(
            username='admin_test',
            password='pass123',
            organization=org,
            role=role,
            status='approved',
        )
        self.assertEqual(user.username, 'admin_test')
        self.assertTrue(user.check_password('pass123'))
        self.assertFalse(user.check_password('mal'))
        self.assertEqual(user.status, 'approved')

    def test_unicidad_usuario_por_organizacion(self):
        org = Organization.objects.create(name='Org', slug='org')
        role = Role.objects.create(name='admin', organization=org)
        User.objects.create_user(
            username='dup', password='pass123',
            organization=org, role=role, status='approved',
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='dup', password='pass123',
                organization=org, role=role, status='approved',
            )
