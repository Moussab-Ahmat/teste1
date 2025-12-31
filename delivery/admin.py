from django.contrib import admin

from delivery.models import DeliveryZone, DeliverySlot, DeliveryFeeRule


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(DeliverySlot)
class DeliverySlotAdmin(admin.ModelAdmin):
    list_display = ('zone', 'day_of_week', 'start_time', 'end_time', 'is_active')
    list_filter = ('zone', 'day_of_week', 'is_active')
    search_fields = ('zone__name',)


@admin.register(DeliveryFeeRule)
class DeliveryFeeRuleAdmin(admin.ModelAdmin):
    list_display = ('zone', 'min_cart_total_xaf', 'max_cart_total_xaf', 'delivery_fee_xaf')
    list_filter = ('zone',)
    search_fields = ('zone__name',)
