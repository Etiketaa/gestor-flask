from django.urls import path
from . import views

urlpatterns = [
    # Campos personalizados
    path('custom-fields', views.CustomFieldDefinitionListCreateView.as_view(), name='custom-field-list-create'),
    path('custom-fields/<int:pk>', views.CustomFieldDefinitionDetailView.as_view(), name='custom-field-detail'),

    # Categorías
    path('categories', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>', views.CategoryDetailView.as_view(), name='category-detail'),

    # Ítems
    path('items', views.ItemListCreateView.as_view(), name='item-list-create'),
    path('items/<int:pk>', views.ItemDetailView.as_view(), name='item-detail'),
]
