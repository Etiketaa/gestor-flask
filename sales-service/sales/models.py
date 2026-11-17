from django.db import models


class CashRegister(models.Model):
    """Caja de una organización. Solo puede haber una abierta a la vez."""
    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Abierta'),
        (STATUS_CLOSED, 'Cerrada'),
    ]

    organization_id = models.IntegerField()
    opened_by = models.IntegerField()  # user_id que abrió la caja
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    opening_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OPEN)

    class Meta:
        db_table = 'cash_registers'
        ordering = ['-opened_at']

    def __str__(self):
        return f"Caja #{self.id} - Org {self.organization_id} ({self.status})"


class CashMovement(models.Model):
    """Movimiento de efectivo dentro de una caja (ingreso/egreso)."""
    TYPE_INCOME = 'income'
    TYPE_EXPENSE = 'expense'
    TYPE_CHOICES = [
        (TYPE_INCOME, 'Ingreso'),
        (TYPE_EXPENSE, 'Egreso'),
    ]

    cash_register = models.ForeignKey(
        CashRegister, on_delete=models.CASCADE, related_name='movements'
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cash_movements'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()} ${self.amount} - Caja #{self.cash_register_id}"


class Client(models.Model):
    """Cliente de la carpintería (obra, particular, etc.)."""
    IVA_RESPONSABLE_INSCRIPTO = 'responsable_inscripto'
    IVA_MONOTRIBUTO = 'monotributo'
    IVA_CONSUMIDOR_FINAL = 'consumidor_final'
    IVA_EXENTO = 'exento'
    IVA_CHOICES = [
        (IVA_RESPONSABLE_INSCRIPTO, 'Responsable Inscripto'),
        (IVA_MONOTRIBUTO, 'Monotributo'),
        (IVA_CONSUMIDOR_FINAL, 'Consumidor Final'),
        (IVA_EXENTO, 'Exento'),
    ]

    organization_id = models.IntegerField()
    name = models.CharField(max_length=200)  # razon social o nombre
    cuit = models.CharField(max_length=20, blank=True, null=True, unique=True)
    iva_condition = models.CharField(max_length=30, choices=IVA_CHOICES, default=IVA_CONSUMIDOR_FINAL)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'clients'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.cuit or 'sin CUIT'})"


class Quote(models.Model):
    """Presupuesto/cotización para un cliente (obra, apertura, etc.)."""
    STATUS_DRAFT = 'draft'
    STATUS_SENT = 'sent'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_EXPIRED = 'expired'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Borrador'),
        (STATUS_SENT, 'Enviado'),
        (STATUS_ACCEPTED, 'Aceptado'),
        (STATUS_REJECTED, 'Rechazado'),
        (STATUS_EXPIRED, 'Expirado'),
    ]

    organization_id = models.IntegerField()
    user_id = models.IntegerField()  # vendedor que creó el presupuesto
    client_name = models.CharField(max_length=200)
    client_cuit = models.CharField(max_length=20, blank=True, null=True)
    client_address = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valid_until = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quotes'
        ordering = ['-created_at']

    def __str__(self):
        return f"Presupuesto #{self.id} - {self.client_name}"


class QuoteItem(models.Model):
    """Ítem de un presupuesto (ej. ventana, puerta, vidrio, herraje)."""
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)  # ej. "Ventana 120x150 aluminio anodizado"
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=50, default='unidad')  # unidad, m2, lm
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    item_id = models.IntegerField(null=True, blank=True)  # referencia opcional a catalog items

    class Meta:
        db_table = 'quote_items'

    def __str__(self):
        return f"{self.description} x{self.quantity}"


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


class Invoice(models.Model):
    """Factura electrónica (AFIP/ARCA). Tipos: A, B."""
    TYPE_A = 'A'
    TYPE_B = 'B'
    TYPE_CHOICES = [
        (TYPE_A, 'Factura A'),
        (TYPE_B, 'Factura B'),
    ]

    STATUS_DRAFT = 'draft'
    STATUS_REQUESTED = 'requested'  # CAE solicitado
    STATUS_ISSUED = 'issued'        # CAE obtenido
    STATUS_CANCELLED = 'cancelled'  # Anulada
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Borrador'),
        (STATUS_REQUESTED, 'Solicitando CAE'),
        (STATUS_ISSUED, 'Emitida'),
        (STATUS_CANCELLED, 'Anulada'),
    ]

    organization_id = models.IntegerField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    quote = models.ForeignKey(Quote, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')

    invoice_type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=TYPE_B)
    point_of_sale = models.IntegerField(default=1)  # punto de venta AFIP
    invoice_number = models.IntegerField(null=True, blank=True)  # numero de comprobante

    cae = models.CharField(max_length=14, blank=True, null=True)  # CAE de AFIP
    cae_expiration_date = models.DateField(null=True, blank=True)  # fecha de vencimiento del CAE

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    issue_date = models.DateTimeField(auto_now_add=True)

    afip_request_xml = models.TextField(blank=True, null=True)   # request enviado a AFIP
    afip_response_xml = models.TextField(blank=True, null=True)  # respuesta de AFIP

    class Meta:
        db_table = 'invoices'
        ordering = ['-issue_date']
        unique_together = ('point_of_sale', 'invoice_number')

    def __str__(self):
        return f"Factura {self.invoice_type} {self.point_of_sale:04d}-{self.invoice_number or 0:08d}"
