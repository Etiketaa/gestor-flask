from django.test import TestCase
from django.utils import timezone
from .models import Sale, SaleItem, InventoryMovement, CashRegister, CashMovement, Quote, QuoteItem


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


class CashRegisterModelTest(TestCase):
    def test_abrir_caja(self):
        caja = CashRegister.objects.create(
            organization_id=1,
            opened_by=1,
            opening_amount=5000,
            status=CashRegister.STATUS_OPEN,
        )
        self.assertEqual(caja.status, 'open')
        self.assertEqual(caja.opening_amount, 5000)
        self.assertIsNotNone(caja.opened_at)

    def test_cerrar_caja(self):
        caja = CashRegister.objects.create(
            organization_id=1,
            opened_by=1,
            opening_amount=5000,
            status=CashRegister.STATUS_OPEN,
        )
        caja.closed_at = timezone.now()
        caja.closing_amount = 6000
        caja.status = CashRegister.STATUS_CLOSED
        caja.save()
        self.assertEqual(caja.status, 'closed')
        self.assertEqual(caja.closing_amount, 6000)
        self.assertIsNotNone(caja.closed_at)


class CashMovementModelTest(TestCase):
    def test_crear_movimiento_caja(self):
        caja = CashRegister.objects.create(
            organization_id=1,
            opened_by=1,
            opening_amount=5000,
            status=CashRegister.STATUS_OPEN,
        )
        movimiento = CashMovement.objects.create(
            cash_register=caja,
            type=CashMovement.TYPE_INCOME,
            amount=1000,
            reason='Venta',
        )
        self.assertEqual(movimiento.amount, 1000)
        self.assertEqual(movimiento.type, 'income')
        self.assertEqual(movimiento.cash_register, caja)
