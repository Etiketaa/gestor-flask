from django.test import TestCase
from .models import Sale, SaleItem, InventoryMovement


class SaleModelTest(TestCase):
    def test_crear_venta(self):
        sale = Sale.objects.create(
            total_amount=90000,
            user_id=1,
            organization_id=1,
        )
        self.assertEqual(sale.total_amount, 90000)
        self.assertEqual(sale.user_id, 1)
        self.assertEqual(sale.organization_id, 1)
        self.assertIsNotNone(sale.sale_date)

    def test_venta_con_items(self):
        sale = Sale.objects.create(
            total_amount=90000, user_id=1, organization_id=1,
        )
        item = SaleItem.objects.create(
            sale=sale, item_id=5, quantity=2, price_per_unit=45000,
        )
        self.assertEqual(sale.items.count(), 1)
        self.assertEqual(item.item_id, 5)
        self.assertEqual(item.quantity, 2)


class InventoryMovementModelTest(TestCase):
    def test_crear_movimiento(self):
        movement = InventoryMovement.objects.create(
            item_id=5,
            quantity_change=-2,
            reason='Venta',
            organization_id=1,
        )
        self.assertEqual(movement.item_id, 5)
        self.assertEqual(movement.quantity_change, -2)
        self.assertEqual(movement.reason, 'Venta')
        self.assertIsNotNone(movement.movement_date)
