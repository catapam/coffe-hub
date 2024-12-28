# Django imports
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Internal imports
from .models import OrderLineItem


@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    '''
    Signal to update the order total when an order line item is saved.

    Args:
        sender: The model class that sent the signal.
        instance: The actual instance being saved.
        created (bool): Whether this is a new instance.
        **kwargs: Additional keyword arguments.
    '''
    instance.order.update_total()


@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    '''
    Signal to update the order total when an order line item is deleted.

    Args:
        sender: The model class that sent the signal.
        instance: The actual instance being deleted.
        **kwargs: Additional keyword arguments.
    '''
    instance.order.update_total()
