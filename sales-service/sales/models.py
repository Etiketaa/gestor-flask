from django.db import models


class Sale(models.Model):
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField()  # sin FK a auth-service
    organization_id = models.IntegerField()

    class Meta:
        db_table = 'sales'

    def __str__(self):
        return f"Venta #{self.id}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    item_id = models.IntegerField()  # referencia a catalog_service.items
    quantity = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'sale_items'


class InventoryMovement(models.Model):
    item_id = models.IntegerField()
    quantity_change = models.IntegerField()
    reason = models.CharField(max_length=200, blank=True, null=True)
    movement_date = models.DateTimeField(auto_now_add=True)
    organization_id = models.IntegerField()

    class Meta:
        db_table = 'inventory_movements'

    def __str__(self):
        return f"Movimiento item {self.item_id}: {self.quantity_change}"
