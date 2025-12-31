from datetime import timedelta

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import OTPCode, OTPVerificationToken, User


class OTPFlowTests(APITestCase):
    def setUp(self):
        self.phone_number = "+23512345678"

    def test_request_otp_respects_rate_limit(self):
        url = reverse("otp-request")
        for _ in range(settings.OTP_MAX_REQUESTS_PER_HOUR):
            response = self.client.post(url, {"phone_number": self.phone_number}, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(url, {"phone_number": self.phone_number}, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_verify_otp_and_create_token(self):
        request_url = reverse("otp-request")
        verify_url = reverse("otp-verify")
        self.client.post(request_url, {"phone_number": self.phone_number}, format="json")
        otp = OTPCode.objects.get(user__phone_number=self.phone_number)

        response = self.client.post(
            verify_url, {"phone_number": self.phone_number, "code": otp.code}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        otp.refresh_from_db()
        self.assertTrue(otp.is_verified)
        self.assertIn("otp_token", response.data)
        self.assertTrue(
            OTPVerificationToken.objects.filter(user__phone_number=self.phone_number, token=response.data["otp_token"])
            .exists()
        )

    def test_verify_otp_rejects_expired_codes(self):
        user = User.objects.create(phone_number=self.phone_number)
        expired = timezone.now() - timedelta(minutes=1)
        otp = OTPCode.objects.create(user=user, code="123456", expires_at=expired)

        verify_url = reverse("otp-verify")
        response = self.client.post(
            verify_url, {"phone_number": self.phone_number, "code": otp.code}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_jwt_auth_requires_valid_otp_token(self):
        request_url = reverse("otp-request")
        verify_url = reverse("otp-verify")
        token_url = reverse("token_obtain_pair")
        refresh_url = reverse("token_refresh")

        self.client.post(request_url, {"phone_number": self.phone_number}, format="json")
        otp = OTPCode.objects.get(user__phone_number=self.phone_number)
        verify_response = self.client.post(
            verify_url, {"phone_number": self.phone_number, "code": otp.code}, format="json"
        )
        otp_token = verify_response.data["otp_token"]

        token_response = self.client.post(
            token_url, {"phone_number": self.phone_number, "otp_token": otp_token}, format="json"
        )
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", token_response.data)
        self.assertIn("access", token_response.data)

        refresh_response = self.client.post(
            refresh_url,
            {"refresh": token_response.data["refresh"], "otp_token": otp_token},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

        invalid_refresh_response = self.client.post(
            token_url, {"phone_number": self.phone_number, "otp_token": "invalid"}, format="json"
        )
        self.assertEqual(invalid_refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
