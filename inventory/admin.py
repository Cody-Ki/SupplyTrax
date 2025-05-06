from django.contrib import admin
from .models import InventoryItem, TransactionLog, Department, Asset

admin.site.register(InventoryItem)
admin.site.register(TransactionLog)
admin.site.register(Department)
admin.site.register(Asset)

