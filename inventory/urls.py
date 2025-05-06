from django.urls import path
from .views import (
    DashboardView,
    InventoryListView,
    InventoryCreateView,
    InventoryUpdateView,
    InventoryDeleteView,
    InventoryDetailView,
    StockAdjustView,
    AssetListView,
    AssetCreateView,
    AssetActionView,
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('inventory/', InventoryListView.as_view(), name='inventory-list'),
    path('inventory/add/', InventoryCreateView.as_view(), name='inventory-add'),
    path('inventory/<int:pk>/', InventoryDetailView.as_view(), name='inventory-detail'),
    path('inventory/<int:pk>/edit/', InventoryUpdateView.as_view(), name='inventory-edit'),
    path('inventory/<int:pk>/delete/', InventoryDeleteView.as_view(), name='inventory-delete'),
    path('inventory/<int:pk>/adjust/', StockAdjustView.as_view(), name='stock-adjust'),
    path('inventory/<int:pk>/assets/', AssetListView.as_view(), name='asset-list'),
    path('inventory/<int:pk>/assets/add/', AssetCreateView.as_view(), name='asset-add'),
    path('inventory/<int:pk>/assets/action/', AssetActionView.as_view(), name='asset-action'),
]
