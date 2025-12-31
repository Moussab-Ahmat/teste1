from django.db.models.signals import post_save
from django.dispatch import receiver

from .cache import invalidate_products_cache
from .models import Product


@receiver(post_save, sender=Product)
def clear_product_cache_on_save(**_kwargs):
    invalidate_products_cache()
