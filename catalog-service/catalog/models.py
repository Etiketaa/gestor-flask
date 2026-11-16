from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    organization_id = models.IntegerField()  # sin FK para acoplamiento débil entre servicios
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        unique_together = ('name', 'organization_id')

    def __str__(self):
        return self.name


class Item(models.Model):
    sku = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=50, default='unidad')
    supplier = models.CharField(max_length=200, blank=True, null=True)
    category_id = models.IntegerField(null=True, blank=True)
    organization_id = models.IntegerField()
    custom_fields = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'items'
        unique_together = ('sku', 'organization_id')

    def __str__(self):
        return self.name
