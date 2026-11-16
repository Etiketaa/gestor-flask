from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Sale, SaleItem, InventoryMovement
from .serializers import SaleSerializer, InventoryMovementSerializer


class SaleListCreateView(APIView):
    def get(self, request):
        org_id = request.query_params.get('organization_id')
        qs = Sale.objects.all()
        if org_id:
            qs = qs.filter(organization_id=org_id)
        qs = qs.order_by('-sale_date')
        return Response(SaleSerializer(qs, many=True).data)

    @transaction.atomic
    def post(self, request):
        data = request.data
        cart = data.get('cart')
        total = data.get('total')
        user_id = data.get('user_id')
        organization_id = data.get('organization_id')

        if not cart or total is None or not user_id or not organization_id:
            return Response({'error': 'Datos de venta incompletos'}, status=status.HTTP_400_BAD_REQUEST)

        sale = Sale.objects.create(
            total_amount=total,
            user_id=user_id,
            organization_id=organization_id,
        )

        for entry in cart:
            SaleItem.objects.create(
                sale=sale,
                item_id=entry.get('item_id'),
                quantity=entry.get('quantity'),
                price_per_unit=entry.get('price'),
            )
            InventoryMovement.objects.create(
                item_id=entry.get('item_id'),
                quantity_change=-entry.get('quantity'),
                reason='Venta',
                organization_id=organization_id,
            )

        return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED)


class SaleDetailView(APIView):
    def get(self, request, pk):
        sale = get_object_or_404(Sale, pk=pk)
        return Response(SaleSerializer(sale).data)


class SaleItemsView(APIView):
    def get(self, request, sale_id):
        sale = get_object_or_404(Sale, pk=sale_id)
        return Response(SaleItemSerializer(sale.items.all(), many=True).data)


class InventoryMovementListView(APIView):
    def get(self, request):
        org_id = request.query_params.get('organization_id')
        item_id = request.query_params.get('item_id')
        qs = InventoryMovement.objects.all()
        if org_id:
            qs = qs.filter(organization_id=org_id)
        if item_id:
            qs = qs.filter(item_id=item_id)
        qs = qs.order_by('-movement_date')
        return Response(InventoryMovementSerializer(qs, many=True).data)
