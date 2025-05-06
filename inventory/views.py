from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, F
from .models import InventoryItem, AssetAssignment
from .forms import AssetAssignmentForm


class AssetAssignView(LoginRequiredMixin, View):
    """
    GET: show check-out/check-in form for asset managed items.
    POST: record the assignment for this asset.
    """
    def get(self, request, pk):
        item = get_object_or_404(InventoryItem, pk=pk, asset_managed=True)
        initial = {'action': request.GET.get('actions', 'checkout')}
        form = AssetAssignmentForm(initial=initial)
        return render(request, 'inventory/asset_assign_form.html', {
            'item': item, 'form': form
        })

    def post(self, request, pk):
        item = get_object_or_404(InventoryItem, pk=pk, asset_managed=True)
        form = AssetAssignmentForm(request.POST)
        if form.is_valid():
            assign = form.save(commit=False)
            assign.item = item
            assign.save()
            return redirect('inventory-detail', pk=pk)
        return render(request, 'inventory/asset_assign_form.html', {
            'item': item, 'form': form
        })
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
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
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
        ctx['search'] = self.request.GET.get('search', '').strip()
        ctx['selected_category'] = self.request.GET.get('category', '')
        ctx['selected_location'] = self.request.GET.get('location', '')
        ctx['selected_sort'] = self.request.GET.get('sort', '')
        ctx['categories'] = InventoryItem.CATEGORY_CHOICES
        ctx['locations'] = InventoryItem.LOCATION_CHOICES
        params = self.request.GET.copy()
        params.pop('page', None)
        ctx['params'] = params.urlencode()
        return ctx


class InventoryCreateView(LoginRequiredMixin, CreateView):
    model = InventoryItem
    fields = ['name', 'description', 'category', 'quantity', 'reorder_threshold', 'supplier_info', 'price', 'location',
              'asset_managed','serial_number', 'barcode']
    template_name = 'inventory/inventory_form.html'
    success_url = reverse_lazy('inventory-list')

    def form_valid(self, form):
        form.instance._user = self.request.user
        return super().form_valid(form)


class InventoryUpdateView(LoginRequiredMixin, UpdateView):
    model = InventoryItem
    fields = ['name', 'description', 'category', 'quantity', 'reorder_threshold', 'supplier_info', 'price', 'location',
              'asset_managed','serial_number', 'barcode']
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
        context = super().get_context_data(**kwargs)
        # Key metrics
        context['total_items'] = InventoryItem.objects.count()
        context['low_stock_items'] = InventoryItem.objects.filter(
            quantity__lte=F('reorder_threshold')
        ).count()

        # Aggregated summaries
        cats = (InventoryItem.objects
                .values('category')
                .annotate(total=Count('id'))
                .order_by('category'))
        locs = (InventoryItem.objects
                .values('location')
                .annotate(total=Count('id'))
                .order_by('location'))

        # Choice mapping
        category_map = dict(InventoryItem.CATEGORY_CHOICES)
        location_map = dict(InventoryItem.LOCATION_CHOICES)

        # Prepare chart data arrays with display labels
        context['category_labels'] = [category_map.get(c['category'], c['category']) for c in cats]
        context['category_data'] = [c['total'] for c in cats]
        context['location_labels'] = [location_map.get(l['location'], l['location']) for l in locs]
        context['location_data'] = [l['total'] for l in locs]

        return context

