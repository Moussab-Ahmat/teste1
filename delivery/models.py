from __future__ import annotations
from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _


class DeliveryZone(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class DeliverySlot(models.Model):
    class WeekDay(models.IntegerChoices):
        MONDAY = 0, _('Monday')
        TUESDAY = 1, _('Tuesday')
        WEDNESDAY = 2, _('Wednesday')
        THURSDAY = 3, _('Thursday')
        FRIDAY = 4, _('Friday')
        SATURDAY = 5, _('Saturday')
        SUNDAY = 6, _('Sunday')

    zone = models.ForeignKey(DeliveryZone, related_name='slots', on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=WeekDay.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['zone_id', 'day_of_week', 'start_time']

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.zone.name} {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class DeliveryFeeRule(models.Model):
    zone = models.ForeignKey(DeliveryZone, related_name='fee_rules', on_delete=models.CASCADE)
    min_cart_total_xaf = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    max_cart_total_xaf = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    delivery_fee_xaf = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ['zone_id', 'min_cart_total_xaf', 'max_cart_total_xaf']
        constraints = [
            models.CheckConstraint(
                check=models.Q(max_cart_total_xaf__isnull=True) | models.Q(max_cart_total_xaf__gt=models.F('min_cart_total_xaf')),
                name='delivery_fee_rule_range_valid',
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.zone.name}: {self.min_cart_total_xaf}-{self.max_cart_total_xaf or '∞'} => {self.delivery_fee_xaf}"
