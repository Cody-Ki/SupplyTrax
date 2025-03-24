from django.contrib import admin
from .models import InventoryItem, TransactionLog

admin.site.register(InventoryItem)
admin.site.register(TransactionLog)

