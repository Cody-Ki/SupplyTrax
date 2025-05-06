# inventory/urls.py
from django.urls import path
from .views import InventoryListView, InventoryCreateView, InventoryUpdateView, InventoryDeleteView, DashboardView, \
    InventoryDetailView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('inventory/', InventoryListView.as_view(), name='inventory-list'),
    path('item/add/', InventoryCreateView.as_view(), name='inventory-add'),
    path('item/<int:pk>/edit/', InventoryUpdateView.as_view(), name='inventory-edit'),
    path('item/<int:pk>/delete/', InventoryDeleteView.as_view(), name='inventory-delete'),
    path('inventory/<int:pk>/', InventoryDetailView.as_view(), name='inventory-detail'),
]
