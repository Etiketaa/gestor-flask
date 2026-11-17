from django.urls import path
from . import views

urlpatterns = [
    path('sales', views.SaleListCreateView.as_view(), name='sale-list-create'),
    path('sales/<int:pk>', views.SaleDetailView.as_view(), name='sale-detail'),
    path('sales/<int:sale_id>/items', views.SaleItemsView.as_view(), name='sale-items'),
    path('inventory-movements', views.InventoryMovementListView.as_view(), name='inventory-movements'),

    # Caja
    path('cash-register/open', views.CashRegisterOpenView.as_view(), name='cash-register-open'),
    path('cash-register/close', views.CashRegisterCloseView.as_view(), name='cash-register-close'),
    path('cash-register/current', views.CashRegisterCurrentView.as_view(), name='cash-register-current'),
    path('cash-register/movement', views.CashMovementCreateView.as_view(), name='cash-movement-create'),
    path('cash-register/movements', views.CashMovementListView.as_view(), name='cash-movement-list'),

    # Presupuestos
    path('quotes', views.QuoteListCreateView.as_view(), name='quote-list-create'),
    path('quotes/<int:pk>', views.QuoteDetailView.as_view(), name='quote-detail'),
    path('quotes/<int:pk>/accept', views.QuoteAcceptView.as_view(), name='quote-accept'),

    # Clientes
    path('clients', views.ClientListCreateView.as_view(), name='client-list-create'),
    path('clients/<int:pk>', views.ClientDetailView.as_view(), name='client-detail'),

    # Facturas (AFIP/ARCA)
    path('invoices', views.InvoiceListCreateView.as_view(), name='invoice-list-create'),
    path('invoices/<int:pk>', views.InvoiceDetailView.as_view(), name='invoice-detail'),
    path('invoices/<int:pk>/request-cae', views.InvoiceRequestCAEView.as_view(), name='invoice-request-cae'),
]
