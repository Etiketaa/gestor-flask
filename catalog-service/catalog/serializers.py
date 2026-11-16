from rest_framework import serializers
from .models import Category, Item, CustomFieldDefinition


class CustomFieldDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomFieldDefinition
        fields = (
            'id', 'name', 'field_type', 'organization_id',
            'is_required', 'options', 'created_at',
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'organization_id', 'created_at')


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = (
            'id', 'sku', 'name', 'description', 'price', 'cost_price',
            'quantity', 'unit', 'supplier', 'category_id',
            'organization_id', 'custom_fields', 'created_at', 'updated_at',
        )
