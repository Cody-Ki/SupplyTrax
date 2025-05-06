from django.db import models
from django.contrib.auth.models import User

class InventoryItem(models.Model):
    CATEGORY_CHOICES = [
        ('office', 'Office Supplies'),
        ('it', 'IT Supplies'),
        ('consumable', 'Consumables'),
        ('maint', 'Maintenance'),
        ('clean', 'Cleaning Supplies'),
        ('furniture', 'Furniture'),
        ('misc', 'Miscellaneous'),
    ]

    LOCATION_CHOICES = [
        ('mfld', 'Marshfield'),
        ('abb', 'Abbotsford'),
        ('plo', 'Plover'),
        ('wr', 'Wisconsin Rapids'),
        ('wau', 'Wausau'),
        ('wh', 'Wausau Warehouse'),
        ('cf', 'Chippewa Falls'),
        ('cam', 'Cameron'),
        ('dul', 'Duluth'),
        ('vir', 'Virginia'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    quantity = models.PositiveIntegerField()
    reorder_threshold = models.PositiveIntegerField(default=0)
    supplier_info = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100, choices=LOCATION_CHOICES)
    asset_managed = models.BooleanField(default=False, help_text='Mark as an asset so it can be assigned to User/Department.')
    serial_number = models.CharField(max_length=100, blank=True, null=True, unique=True, help_text='Serial Number or Asset Tag #')
    barcode = models.CharField(max_length=10, blank=True, null=True, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} ({self.quantity})'

class TransactionLog(models.Model):
    ACTION_CHOICES = [
        ('add', 'Add'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]

    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.SET_NULL, #Preserve Log
        null=True,
        blank=True,
        related_name='transactions',
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else 'Unknown User'
        item_name = self.inventory_item.name if self.inventory_item else 'Deleted Item'
        return f'{self.action_type.title()} - {item_name} by {username} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}'