from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import InventoryItem, TransactionLog
from django.contrib.auth.models import User

@receiver(post_save, sender=InventoryItem)
def log_inventory_save(sender, instance, created, **kwargs):
    action = 'add' if created else 'update'
    TransactionLog.objects.create(
        inventory_item=instance,
        user=getattr(instance, '_user', None),
        action_type=action,
    )

@receiver(post_delete, sender=InventoryItem)
def log_inventory_delete(sender, instance, **kwargs):
    TransactionLog.objects.create(
        inventory_item=None,  # Item deleted, so None
        user=getattr(instance, '_user', None),
        action_type='delete',
    )
