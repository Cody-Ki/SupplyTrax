
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView,
    ListView, TemplateView, UpdateView, View
)

from .models import Asset, Department, InventoryItem, TransactionLog

class StockAdjustmentForm(forms.Form):
    delta = forms.IntegerField(
        label="Quantity change",
        help_text="Enter positive to add stock, negative to remove."
    )
    notes = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="Optional note for this adjustment."
    )

class AssetActionForm(forms.Form):
    asset = forms.ModelChoiceField(
        queryset=Asset.objects.none(),
        label="Asset Serial",
    )
    user = forms.ModelChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        label="Assign to user",
    )
    department = forms.ModelChoiceField(
        queryset = Department.objects.all(),
        required = False,
        label="Or assign to department",
    )
    notes = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="Optional note."
    )

class StockAdjustView(LoginRequiredMixin, View):
    def get(self, request, pk):
        item = get_object_or_404(InventoryItem, pk=pk, asset_managed=False)
        form = StockAdjustmentForm()
        return render(request, 'inventory/stock_adjust_form.html', {
            'item': item, 'form': form
        })

    def post(self, request, pk):
        item = get_object_or_404(InventoryItem, pk=pk, asset_managed=False)
        form = StockAdjustmentForm(request.POST)
        if not form.is_valid():
            return render(request, 'inventory/stock_adjust_form.html', {
                'item': item, 'form': form
            })

        delta = form.cleaned_data['delta']
        notes = form.cleaned_data['notes']

        if item.quantity + delta < 0:
            messages.error(request, "Cannot reduce below zero.")
            return redirect('inventory-detail', pk=pk)

        # apply change
        item.quantity = F('quantity') + delta
        item.save(update_fields=['quantity'])

        # log it
        TransactionLog.objects.create(
            inventory_item=item,
            user=request.user,
            action_type='add' if delta > 0 else 'remove',
            delta=delta,
            notes=notes
        )

        messages.success(request, f"Inventory adjusted by {delta}.")
        return redirect('inventory-detail', pk=pk)

class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'inventory/asset_list.html'
    context_object_name = 'assets'

    def get_queryset(self):
        self.item = get_object_or_404(
            InventoryItem, pk=self.kwargs['pk'], asset_managed=True
        )
        return self.item.assets.all()

    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx['item'] = self.item
        return ctx

class AssetCreateView(LoginRequiredMixin, CreateView):
    model = Asset
    fields = ['serial_number']
    template_name = 'inventory/asset_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.item = get_object_or_404(
            InventoryItem, pk=kwargs['pk'], asset_managed=True
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.inventory_item = self.item
        messages.success(
            self.request,
            f"Added asset {form.cleaned_data['serial_number']!r}."
        )
        return super().form_valid(form)

    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx['item'] = self.item
        return ctx

    def get_success_url(self):
        return reverse_lazy('asset-list', args=[self.item.pk])

class AssetActionView(LoginRequiredMixin, View):
    def get(self, request, pk):
        item = get_object_or_404(InventoryItem, pk=pk, asset_managed=True)
        action = request.GET.get('action', 'checkout')
        qs = item.assets.filter(is_checked_out=(action != 'checkout'))
        form = AssetActionForm(initial={'asset': None})
        form.fields['asset'].queryset = qs
        return render(request, 'inventory/asset_action_form.html', {
            'item': item, 'form': form, 'action': action
        })

    def post(self, request, pk):
        item = get_object_or_404(InventoryItem, pk=pk, asset_managed=True)
        action = request.GET.get('action', 'checkout')
        form = AssetActionForm(request.POST)
        form.fields['asset'].queryset = item.assets.filter(
            is_checked_out=(action != 'checkout')
        )

        if not form.is_valid():
            return render(request, 'inventory/asset_action_form.html', {
                'item': item, 'form': form, 'action': action
            })

        asset = form.cleaned_data['asset']
        user  = form.cleaned_data['user']
        department = form.cleaned_data['department']
        notes = form.cleaned_data['notes']

        asset.is_checked_out = (action == 'checkout')
        asset.save(update_fields=['is_checked_out'])

        TransactionLog.objects.create(
            inventory_item=item,
            asset=asset,
            user=user,
            department=department,
            action_type=action,
            notes=notes
        )

        messages.success(request, f"Asset {action} recorded.")
        return redirect('inventory-detail', pk=pk)

class InventoryListView(LoginRequiredMixin, ListView):
    model = InventoryItem
    template_name = 'inventory/inventory_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search', '').strip()
        category = self.request.GET.get('category', '')
        location = self.request.GET.get('location', '')
        sort = self.request.GET.get('sort', '')

        if search:
            qs = qs.filter(Q(name__icontains=search) |
                           Q(description__icontains=search))
        if category:
            qs = qs.filter(category=category)
        if location:
            qs = qs.filter(location=location)
        if sort == 'quantity_asc':
            qs = qs.order_by('quantity')
        elif sort == 'quantity_desc':
            qs = qs.order_by('-quantity')
        elif sort == 'price_asc':
            qs = qs.order_by('price')
        elif sort == 'price_desc':
            qs = qs.order_by('-price')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'search': self.request.GET.get('search', '').strip(),
            'selected_category': self.request.GET.get('category', ''),
            'selected_location': self.request.GET.get('location', ''),
            'selected_sort': self.request.GET.get('sort', ''),
            'categories': InventoryItem.CATEGORY_CHOICES,
            'locations': InventoryItem.LOCATION_CHOICES,
            'params': self.request.GET.copy().urlencode().replace('page=', '')
        })
        return ctx


class InventoryCreateView(LoginRequiredMixin, CreateView):
    model = InventoryItem
    fields = [
        'name','description','category','quantity','reorder_threshold',
        'supplier_info','price','location','asset_managed','barcode'
    ]
    template_name = 'inventory/inventory_form.html'
    success_url   = reverse_lazy('inventory-list')

    def form_valid(self, form):
        form.instance._user = self.request.user
        return super().form_valid(form)


class InventoryUpdateView(LoginRequiredMixin, UpdateView):
    model = InventoryItem
    fields = [
        'name','description','category','quantity','reorder_threshold',
        'supplier_info','price','location','asset_managed','barcode'
    ]
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


class InventoryDetailView(LoginRequiredMixin, DetailView):
    model = InventoryItem
    template_name = 'inventory/inventory_detail.html'
    context_object_name = 'item'


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_items'] = InventoryItem.objects.count()
        ctx['low_stock_items'] = InventoryItem.objects.filter(
            quantity__lte=F('reorder_threshold')
        ).count()

        cats = InventoryItem.objects.values('category') \
              .annotate(total=Count('id')).order_by('category')
        locs = InventoryItem.objects.values('location') \
              .annotate(total=Count('id')).order_by('location')

        cmap = dict(InventoryItem.CATEGORY_CHOICES)
        lmap = dict(InventoryItem.LOCATION_CHOICES)

        ctx['category_labels'] = [cmap[c['category']] for c in cats]
        ctx['category_data'] = [c['total'] for c in cats]
        ctx['location_labels'] = [lmap[l['location']] for l in locs]
        ctx['location_data'] = [l['total'] for l in locs]
        return ctx
