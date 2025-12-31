from rest_framework import serializers

from delivery.models import DeliveryZone, DeliverySlot


class DeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryZone
        fields = ['id', 'name', 'description']


class DeliverySlotSerializer(serializers.ModelSerializer):
    zone_id = serializers.IntegerField(source='zone.id', read_only=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True)

    class Meta:
        model = DeliverySlot
        fields = ['id', 'zone_id', 'zone_name', 'day_of_week', 'start_time', 'end_time', 'is_active']
