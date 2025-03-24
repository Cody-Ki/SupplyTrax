# inventory/urls.py
from django.urls import path
from .views import InventoryListView, InventoryCreateView, InventoryUpdateView, InventoryDeleteView

urlpatterns = [
    path('', InventoryListView.as_view(), name='inventory-list'),
    path('item/add/', InventoryCreateView.as_view(), name='inventory-add'),
    path('item/<int:pk>/edit/', InventoryUpdateView.as_view(), name='inventory-edit'),
    path('item/<int:pk>/delete/', InventoryDeleteView.as_view(), name='inventory-delete'),
]
