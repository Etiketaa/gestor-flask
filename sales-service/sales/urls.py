from django.urls import path
from . import views

urlpatterns = [
    path('sales', views.SaleListCreateView.as_view(), name='sale-list-create'),
    path('sales/<int:pk>', views.SaleDetailView.as_view(), name='sale-detail'),
    path('sales/<int:sale_id>/items', views.SaleItemsView.as_view(), name='sale-items'),
    path('inventory-movements', views.InventoryMovementListView.as_view(), name='inventory-movements'),
]
