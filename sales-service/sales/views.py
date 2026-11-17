from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from .models import Sale, SaleItem, InventoryMovement, CashRegister, CashMovement, Quote, QuoteItem, Client, Invoice
from .serializers import (
    SaleSerializer, InventoryMovementSerializer,
    CashRegisterSerializer, CashMovementSerializer,
    QuoteSerializer, QuoteItemSerializer, ClientSerializer,
    InvoiceSerializer,
)


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


# ---------------- Caja ----------------

class CashRegisterOpenView(APIView):
    def post(self, request):
        data = request.data
        organization_id = data.get('organization_id')
        user_id = data.get('user_id')
        opening_amount = data.get('opening_amount', 0)

        if not organization_id or not user_id:
            return Response({'error': 'organization_id y user_id son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

        # No permitir más de una caja abierta por organización
        if CashRegister.objects.filter(organization_id=organization_id, status=CashRegister.STATUS_OPEN).exists():
            return Response({'error': 'Ya hay una caja abierta para esta organización'}, status=status.HTTP_400_BAD_REQUEST)

        register = CashRegister.objects.create(
            organization_id=organization_id,
            opened_by=user_id,
            opening_amount=opening_amount,
            status=CashRegister.STATUS_OPEN,
        )
        return Response(CashRegisterSerializer(register).data, status=status.HTTP_201_CREATED)


class CashRegisterCloseView(APIView):
    def post(self, request):
        data = request.data
        organization_id = data.get('organization_id')
        closing_amount = data.get('closing_amount')

        if not organization_id:
            return Response({'error': 'organization_id es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)

        register = CashRegister.objects.filter(
            organization_id=organization_id, status=CashRegister.STATUS_OPEN
        ).first()
        if not register:
            return Response({'error': 'No hay caja abierta para esta organización'}, status=status.HTTP_400_BAD_REQUEST)

        register.closed_at = timezone.now()
        register.closing_amount = closing_amount if closing_amount is not None else 0
        register.status = CashRegister.STATUS_CLOSED
        register.save()
        return Response(CashRegisterSerializer(register).data)


class CashRegisterCurrentView(APIView):
    def get(self, request):
        organization_id = request.query_params.get('organization_id')
        if not organization_id:
            return Response({'error': 'organization_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        register = CashRegister.objects.filter(
            organization_id=organization_id, status=CashRegister.STATUS_OPEN
        ).first()
        if not register:
            return Response({'error': 'No hay caja abierta para esta organización'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CashRegisterSerializer(register).data)


class CashMovementCreateView(APIView):
    def post(self, request):
        data = request.data
        cash_register_id = data.get('cash_register_id')
        movement_type = data.get('type')
        amount = data.get('amount')
        reason = data.get('reason')

        if not all([cash_register_id, movement_type, amount, reason]):
            return Response({'error': 'cash_register_id, type, amount y reason son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

        if movement_type not in (CashMovement.TYPE_INCOME, CashMovement.TYPE_EXPENSE):
            return Response({'error': 'type debe ser income o expense'}, status=status.HTTP_400_BAD_REQUEST)

        register = get_object_or_404(CashRegister, pk=cash_register_id)
        movement = CashMovement.objects.create(
            cash_register=register,
            type=movement_type,
            amount=amount,
            reason=reason,
        )
        return Response(CashMovementSerializer(movement).data, status=status.HTTP_201_CREATED)


class CashMovementListView(APIView):
    def get(self, request):
        cash_register_id = request.query_params.get('cash_register_id')
        qs = CashMovement.objects.all()
        if cash_register_id:
            qs = qs.filter(cash_register_id=cash_register_id)
        qs = qs.order_by('-created_at')
        return Response(CashMovementSerializer(qs, many=True).data)


# ---------------- Presupuestos ----------------

class QuoteListCreateView(APIView):
    def get(self, request):
        org_id = request.query_params.get('organization_id')
        status = request.query_params.get('status')
        qs = Quote.objects.all()
        if org_id:
            qs = qs.filter(organization_id=org_id)
        if status:
            qs = qs.filter(status=status)
        qs = qs.order_by('-created_at')
        return Response(QuoteSerializer(qs, many=True).data)

    def post(self, request):
        data = request.data
        organization_id = data.get('organization_id')
        user_id = data.get('user_id')
        client_name = data.get('client_name')
        items = data.get('items', [])
        valid_until = data.get('valid_until')
        notes = data.get('notes', '')

        if not organization_id or not user_id or not client_name:
            return Response({'error': 'organization_id, user_id y client_name son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

        subtotal = 0
        tax_amount = 0
        for it in items:
            qty = Decimal(str(it.get('quantity', 1)))
            price = Decimal(str(it.get('price_per_unit', 0)))
            subtotal += qty * price
        tax_amount = subtotal * Decimal('0.21')  # IVA 21% Argentina

        quote = Quote.objects.create(
            organization_id=organization_id,
            user_id=user_id,
            client_name=client_name,
            client_cuit=data.get('client_cuit', ''),
            client_address=data.get('client_address', ''),
            status=data.get('status', Quote.STATUS_DRAFT),
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=subtotal + tax_amount,
            valid_until=valid_until,
            notes=notes,
        )

        for it in items:
            QuoteItem.objects.create(
                quote=quote,
                description=it.get('description', ''),
                quantity=Decimal(str(it.get('quantity', 1))),
                unit=it.get('unit', 'unidad'),
                price_per_unit=Decimal(str(it.get('price_per_unit', 0))),
                item_id=it.get('item_id'),
            )

        return Response(QuoteSerializer(quote).data, status=status.HTTP_201_CREATED)


class QuoteDetailView(APIView):
    def get(self, request, pk):
        quote = get_object_or_404(Quote, pk=pk)
        return Response(QuoteSerializer(quote).data)

    def put(self, request, pk):
        quote = get_object_or_404(Quote, pk=pk)
        data = request.data
        for field in ('client_name', 'client_cuit', 'client_address', 'status', 'valid_until', 'notes'):
            if field in data:
                setattr(quote, field, data[field])
        quote.save()
        return Response(QuoteSerializer(quote).data)

    def delete(self, request, pk):
        quote = get_object_or_404(Quote, pk=pk)
        quote.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class QuoteAcceptView(APIView):
    def post(self, request, pk):
        quote = get_object_or_404(Quote, pk=pk)
        if quote.status != Quote.STATUS_SENT:
            return Response({'error': 'Solo se puede aceptar un presupuesto enviado'}, status=status.HTTP_400_BAD_REQUEST)
        quote.status = Quote.STATUS_ACCEPTED
        quote.save()
        return Response(QuoteSerializer(quote).data)


# ---------------- Clientes ----------------

class ClientListCreateView(APIView):
    def get(self, request):
        org_id = request.query_params.get('organization_id')
        qs = Client.objects.all()
        if org_id:
            qs = qs.filter(organization_id=org_id)
        qs = qs.order_by('name')
        return Response(ClientSerializer(qs, many=True).data)

    def post(self, request):
        data = request.data
        organization_id = data.get('organization_id')
        name = data.get('name')
        if not organization_id or not name:
            return Response({'error': 'organization_id y name son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)
        client = Client.objects.create(
            organization_id=organization_id,
            name=name,
            cuit=data.get('cuit', ''),
            iva_condition=data.get('iva_condition', Client.IVA_CONSUMIDOR_FINAL),
            address=data.get('address', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
        )
        return Response(ClientSerializer(client).data, status=status.HTTP_201_CREATED)


class ClientDetailView(APIView):
    def get(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        return Response(ClientSerializer(client).data)

    def put(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        data = request.data
        for field in ('name', 'cuit', 'iva_condition', 'address', 'phone', 'email'):
            if field in data:
                setattr(client, field, data[field])
        client.save()
        return Response(ClientSerializer(client).data)

    def delete(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        client.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------- Facturas (AFIP/ARCA) ----------------

class InvoiceListCreateView(APIView):
    def get(self, request):
        org_id = request.query_params.get('organization_id')
        status = request.query_params.get('status')
        qs = Invoice.objects.all()
        if org_id:
            qs = qs.filter(organization_id=org_id)
        if status:
            qs = qs.filter(status=status)
        qs = qs.order_by('-issue_date')
        return Response(InvoiceSerializer(qs, many=True).data)

    def post(self, request):
        data = request.data
        organization_id = data.get('organization_id')
        client_id = data.get('client')
        invoice_type = data.get('invoice_type', Invoice.TYPE_B)

        if not organization_id or not client_id:
            return Response({'error': 'organization_id y client son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

        invoice = Invoice.objects.create(
            organization_id=organization_id,
            client_id=client_id,
            sale_id=data.get('sale'),
            quote_id=data.get('quote'),
            invoice_type=invoice_type,
            point_of_sale=data.get('point_of_sale', 1),
            subtotal=data.get('subtotal', 0),
            tax_amount=data.get('tax_amount', 0),
            total_amount=data.get('total_amount', 0),
            status=Invoice.STATUS_DRAFT,
        )
        return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)


class InvoiceDetailView(APIView):
    def get(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        return Response(InvoiceSerializer(invoice).data)

    def put(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        data = request.data
        for field in ('invoice_type', 'point_of_sale', 'subtotal', 'tax_amount',
                      'total_amount', 'status', 'cae', 'cae_expiration_date',
                      'afip_request_xml', 'afip_response_xml'):
            if field in data:
                setattr(invoice, field, data[field])
        invoice.save()
        return Response(InvoiceSerializer(invoice).data)

    def delete(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        invoice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvoiceRequestCAEView(APIView):
    """Solicita CAE a AFIP (placeholder: sin certificado real no se puede probar)."""
    def post(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        if invoice.status != Invoice.STATUS_DRAFT:
            return Response({'error': 'Solo se puede solicitar CAE para facturas en borrador'}, status=status.HTTP_400_BAD_REQUEST)

        # Placeholder: aquí iría la llamada a WSAA + WSFEv1 de AFIP
        # Requiere certificado digital (.p12) y CUIT de la organización
        invoice.status = Invoice.STATUS_REQUESTED
        invoice.afip_request_xml = '<placeholder>WSAA login + WSFEv1 FECAESolicitar</placeholder>'
        invoice.save()
        return Response(InvoiceSerializer(invoice).data)
