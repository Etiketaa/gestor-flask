from django.test import TestCase
from .models import Category, Item, CustomFieldDefinition


class CustomFieldDefinitionModelTest(TestCase):
    def test_crear_campo_personalizado(self):
        field = CustomFieldDefinition.objects.create(
            name='Talle',
            field_type='select',
            organization_id=1,
            is_required=True,
            options=['S', 'M', 'L'],
        )
        self.assertEqual(field.name, 'Talle')
        self.assertEqual(field.field_type, 'select')
        self.assertEqual(field.organization_id, 1)
        self.assertTrue(field.is_required)
        self.assertEqual(field.options, ['S', 'M', 'L'])

    def test_unicidad_nombre_por_organizacion(self):
        CustomFieldDefinition.objects.create(
            name='Dup', field_type='text', organization_id=1,
        )
        with self.assertRaises(Exception):
            CustomFieldDefinition.objects.create(
                name='Dup', field_type='text', organization_id=1,
            )


class CategoryModelTest(TestCase):
    def test_crear_categoria(self):
        cat = Category.objects.create(
            name='Herramientas', organization_id=1
        )
        self.assertEqual(cat.name, 'Herramientas')
        self.assertEqual(cat.organization_id, 1)

    def test_unicidad_categoria_por_organizacion(self):
        Category.objects.create(name='Dup', organization_id=1)
        with self.assertRaises(Exception):
            Category.objects.create(name='Dup', organization_id=1)


class ItemModelTest(TestCase):
    def test_crear_item(self):
        item = Item.objects.create(
            sku='PROD-001',
            name='Martillo',
            price=4500,
            cost_price=3000,
            quantity=10,
            unit='unidad',
            organization_id=1,
            custom_fields={'material': 'acero'},
        )
        self.assertEqual(item.sku, 'PROD-001')
        self.assertEqual(item.name, 'Martillo')
        self.assertEqual(item.quantity, 10)
        self.assertEqual(item.custom_fields, {'material': 'acero'})

    def test_unicidad_sku_por_organizacion(self):
        Item.objects.create(
            sku='DUP-001', name='Dup', price=100,
            quantity=1, organization_id=1,
        )
        with self.assertRaises(Exception):
            Item.objects.create(
                sku='DUP-001', name='Dup2', price=200,
                quantity=1, organization_id=1,
            )
