from rest_framework import generics

from delivery.models import DeliveryZone, DeliverySlot
from delivery.serializers import DeliveryZoneSerializer, DeliverySlotSerializer


class DeliveryZoneListView(generics.ListAPIView):
    queryset = DeliveryZone.objects.all().order_by('name')
    serializer_class = DeliveryZoneSerializer


class DeliverySlotListView(generics.ListAPIView):
    serializer_class = DeliverySlotSerializer

    def get_queryset(self):
        queryset = DeliverySlot.objects.filter(is_active=True)
        zone_id = self.request.query_params.get('zone_id')
        if zone_id:
            queryset = queryset.filter(zone_id=zone_id)
        return queryset.order_by('day_of_week', 'start_time')
