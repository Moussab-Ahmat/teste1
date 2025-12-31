from django.urls import path

from .views import (
    OTPRequestView,
    OTPTokenObtainPairView,
    OTPTokenRefreshView,
    OTPVerifyView,
)

urlpatterns = [
    path("otp/request/", OTPRequestView.as_view(), name="otp-request"),
    path("otp/verify/", OTPVerifyView.as_view(), name="otp-verify"),
    path("token/", OTPTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", OTPTokenRefreshView.as_view(), name="token_refresh"),
]
