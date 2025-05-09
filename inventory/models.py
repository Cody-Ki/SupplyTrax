# inventory/models.py

from django.db import models
from django.conf import settings

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
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    reorder_threshold = models.PositiveIntegerField(default=0)
    supplier_info = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    barcode = models.CharField(max_length=100, blank=True)

    quantity = models.PositiveIntegerField(default=0)

    asset_managed = models.BooleanField(
        default=False,
        help_text="If true, we track individual serials as Assets instead of adjusting quantity directly."
    )

    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def available_quantity(self):
        if self.asset_managed:
            return self.assets.filter(is_checked_out=False).count()
        return self.quantity

    @property
    def last_asset_transaction(self):
        return self.transactions.filter(
            action_type__in=["checkout", "checkin"]
        ).order_by("-timestamp").first()


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Asset(models.Model):
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name="assets"
    )
    serial_number  = models.CharField(max_length=100, unique=True, help_text="Serial Number or Asset Tag")
    is_checked_out = models.BooleanField(default=False)

    @property
    def current_user(self):
        last = self.transactionlog_set.filter(action_type="checkout").order_by("-timestamp").first()
        return last.user if last else None

    def __str__(self):
        return f"{self.inventory_item.name} - {self.serial_number}"

    class Meta:
        ordering = ["inventory_item", "serial_number"]

    def __str__(self):
        return f"{self.inventory_item.name} [{self.serial_number}]"


class TransactionLog(models.Model):
    ACTION_CHOICES = [
        ("add", "Add stock"),
        ("remove", "Remove stock"),
        ("checkout", "Check‐out asset"),
        ("checkin", "Check‐in asset"),
        ("update", "Update item"),
        ("delete", "Delete item"),
    ]

    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    department     = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)
    delta = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Option note for transaction")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        who = self.user.username if self.user else (
            self.department.name if self.department else "Unknown"
        )
        what = self.asset.serial_number if self.asset else self.inventory_item.name
        return f"{self.get_action_type_display()} {what} by {who} on {self.timestamp:%Y-%m-%d %H:%M}"

