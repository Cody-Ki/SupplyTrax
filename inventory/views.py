# inventory/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import InventoryItem

class InventoryListView(LoginRequiredMixin, ListView):
    model = InventoryItem
    template_name = 'inventory/inventory_list.html'
    context_object_name = 'items'

class InventoryCreateView(LoginRequiredMixin, CreateView):
    model = InventoryItem
    fields = ['name', 'description', 'category', 'quantity', 'reorder_threshold', 'supplier_info', 'price', 'location', 'barcode']
    template_name = 'inventory/inventory_form.html'
    success_url = reverse_lazy('inventory-list')

    def form_valid(self, form):
        form.instance._user = self.request.user
        return super().form_valid(form)

class InventoryUpdateView(LoginRequiredMixin, UpdateView):
    model = InventoryItem
    fields = ['name', 'description', 'category', 'quantity', 'reorder_threshold', 'supplier_info', 'price', 'location', 'barcode']
    template_name = 'inventory/inventory_form.html'
    success_url = reverse_lazy('inventory-list')

    def form_valid(self, form):
        form.instance._user = self.request.user
        return super().form_valid(form)

class InventoryDeleteView(LoginRequiredMixin, DeleteView):
    model = InventoryItem
    template_name = 'inventory/inventory_confirm_delete.html'
    success_url = reverse_lazy('inventory-list')

    def form_valid(self, form):
        self.object._user = self.request.user
        return super().form_valid(form)
