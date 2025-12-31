from __future__ import annotations
from decimal import Decimal

from django.db.models import Q

from delivery.models import DeliveryFeeRule


def calculate_delivery_fee(zone_id: int, cart_total_xaf: Decimal | float | int | str) -> Decimal | None:
    total = Decimal(cart_total_xaf)
    rule = (
        DeliveryFeeRule.objects.filter(zone_id=zone_id, min_cart_total_xaf__lte=total)
        .filter(Q(max_cart_total_xaf__gte=total) | Q(max_cart_total_xaf__isnull=True))
        .order_by('min_cart_total_xaf', 'max_cart_total_xaf')
        .first()
    )
    return rule.delivery_fee_xaf if rule else None
