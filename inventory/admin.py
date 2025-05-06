from django.contrib import admin
from .models import InventoryItem, TransactionLog, Department, AssetAssignment

admin.site.register(InventoryItem)
admin.site.register(TransactionLog)
admin.site.register(Department)
admin.site.register(AssetAssignment)

