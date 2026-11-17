from rest_framework import serializers
from .models import Sale, SaleItem, InventoryMovement, CashRegister, CashMovement, Quote, QuoteItem, Client, Invoice


class CashRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashRegister
        fields = (
            'id', 'organization_id', 'opened_by', 'opened_at', 'closed_at',
            'opening_amount', 'closing_amount', 'status',
        )


class CashMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashMovement
        fields = (
            'id', 'cash_register', 'type', 'amount', 'reason', 'created_at',
        )


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'organization_id', 'name', 'cuit', 'iva_condition',
                  'address', 'phone', 'email', 'created_at')


class QuoteItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteItem
        fields = ('id', 'description', 'quantity', 'unit', 'price_per_unit', 'item_id')


class QuoteSerializer(serializers.ModelSerializer):
    items = QuoteItemSerializer(many=True, read_only=True)

    class Meta:
        model = Quote
        fields = (
            'id', 'organization_id', 'user_id', 'client_name', 'client_cuit',
            'client_address', 'status', 'subtotal', 'tax_amount', 'total_amount',
            'valid_until', 'notes', 'created_at', 'updated_at', 'items',
        )


class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = ('id', 'item_id', 'quantity', 'price_per_unit')


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = ('id', 'total_amount', 'sale_date', 'user_id', 'organization_id', 'items')


class InventoryMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryMovement
        fields = ('id', 'item_id', 'quantity_change', 'reason', 'movement_date', 'organization_id')


class InvoiceSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)

    class Meta:
        model = Invoice
        fields = (
            'id', 'organization_id', 'client', 'client_name', 'sale', 'quote',
            'invoice_type', 'point_of_sale', 'invoice_number',
            'cae', 'cae_expiration_date',
            'subtotal', 'tax_amount', 'total_amount',
            'status', 'issue_date',
            'afip_request_xml', 'afip_response_xml',
        )
