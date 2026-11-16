from rest_framework import serializers
from .models import Sale, SaleItem, InventoryMovement


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
