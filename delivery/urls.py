from django.urls import path

from delivery.views import DeliveryZoneListView, DeliverySlotListView

urlpatterns = [
    path('zones', DeliveryZoneListView.as_view(), name='delivery-zone-list'),
    path('slots', DeliverySlotListView.as_view(), name='delivery-slot-list'),
]
