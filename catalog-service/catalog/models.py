from django.db import models


class CustomFieldDefinition(models.Model):
    """Define un campo personalizado que una organización puede usar en sus ítems."""
    FIELD_TYPES = [
        ('text', 'Texto'),
        ('number', 'Número'),
        ('select', 'Selección múltiple'),
        ('boolean', 'Sí / No'),
        ('date', 'Fecha'),
    ]

    name = models.CharField(max_length=100)  # ej. "Talle", "Color", "Voltaje"
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, default='text')
    organization_id = models.IntegerField()
    is_required = models.BooleanField(default=False)
    options = models.JSONField(default=list, blank=True)  # solo para select: ["S", "M", "L"]
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'custom_field_definitions'
        unique_together = ('name', 'organization_id')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_field_type_display()})"


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
