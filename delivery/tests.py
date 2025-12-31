from datetime import time
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from delivery.models import DeliveryZone, DeliveryFeeRule, DeliverySlot
from delivery.services import calculate_delivery_fee


class DeliveryFeeRuleTests(TestCase):
    def setUp(self):
        self.zone = DeliveryZone.objects.create(name='Zone A')
        DeliveryFeeRule.objects.create(zone=self.zone, min_cart_total_xaf=Decimal('0'), max_cart_total_xaf=Decimal('10000'), delivery_fee_xaf=Decimal('500'))
        DeliveryFeeRule.objects.create(zone=self.zone, min_cart_total_xaf=Decimal('10000'), max_cart_total_xaf=Decimal('50000'), delivery_fee_xaf=Decimal('300'))
        DeliveryFeeRule.objects.create(zone=self.zone, min_cart_total_xaf=Decimal('50000'), max_cart_total_xaf=None, delivery_fee_xaf=Decimal('0'))

    def test_fee_selected_by_cart_total(self):
        self.assertEqual(calculate_delivery_fee(self.zone.id, Decimal('5000')), Decimal('500'))
        self.assertEqual(calculate_delivery_fee(self.zone.id, Decimal('15000')), Decimal('300'))
        self.assertEqual(calculate_delivery_fee(self.zone.id, Decimal('50000')), Decimal('0'))
        self.assertEqual(calculate_delivery_fee(self.zone.id, Decimal('75000')), Decimal('0'))

    def test_no_rule_returns_none(self):
        other_zone = DeliveryZone.objects.create(name='Zone B')
        self.assertIsNone(calculate_delivery_fee(other_zone.id, Decimal('1000')))


class DeliverySlotAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.zone_a = DeliveryZone.objects.create(name='Zone A')
        self.zone_b = DeliveryZone.objects.create(name='Zone B')
        DeliverySlot.objects.create(zone=self.zone_a, day_of_week=DeliverySlot.WeekDay.MONDAY, start_time=time(8), end_time=time(10), is_active=True)
        DeliverySlot.objects.create(zone=self.zone_a, day_of_week=DeliverySlot.WeekDay.MONDAY, start_time=time(10), end_time=time(12), is_active=False)
        DeliverySlot.objects.create(zone=self.zone_b, day_of_week=DeliverySlot.WeekDay.TUESDAY, start_time=time(9), end_time=time(11), is_active=True)

    def test_filter_slots_by_zone(self):
        url = reverse('delivery-slot-list')
        response = self.client.get(url, {'zone_id': self.zone_a.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        slot = response.data[0]
        self.assertEqual(slot['zone_id'], self.zone_a.id)
        self.assertEqual(slot['day_of_week'], DeliverySlot.WeekDay.MONDAY)

    def test_returns_only_active_slots(self):
        url = reverse('delivery-slot-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertTrue(all(slot['is_active'] for slot in response.data))
