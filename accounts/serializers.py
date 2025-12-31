import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from .models import PHONE_PREFIX, OTPCode, OTPSendLog, OTPVerificationToken

User = get_user_model()


class OTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate_phone_number(self, value: str):
        if not value.startswith(PHONE_PREFIX):
            raise serializers.ValidationError("Phone number must start with +235")
        if len(value) != len(PHONE_PREFIX) + 8 or not value[len(PHONE_PREFIX) :].isdigit():
            raise serializers.ValidationError("Phone number must include 8 digits after +235")
        return value

    def save(self, **kwargs):
        phone_number = self.validated_data["phone_number"]
        user, _ = User.objects.get_or_create(phone_number=phone_number, defaults={"role": User.Roles.CUSTOMER})

        window_start = timezone.now() - timedelta(hours=1)
        request_count = OTPCode.objects.filter(user=user, created_at__gte=window_start).count()
        if request_count >= settings.OTP_MAX_REQUESTS_PER_HOUR:
            raise serializers.ValidationError(
                "OTP request limit reached. Please try again later.", code="rate_limit"
            )

        code = f"{random.randint(0, 999999):06d}"
        expires_at = timezone.now() + timedelta(minutes=settings.OTP_CODE_EXPIRY_MINUTES)
        otp = OTPCode.objects.create(user=user, code=code, expires_at=expires_at)

        OTPSendLog.objects.create(phone_number=phone_number, message=f"Your verification code is {code}")
        return otp


class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        code = attrs.get("code")
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError({"phone_number": "Unknown phone number"}) from exc

        otp = (
            OTPCode.objects.filter(user=user, code=code)
            .order_by("-created_at")
            .first()
        )
        if not otp:
            raise serializers.ValidationError({"code": "Invalid code"})
        if otp.is_expired:
            raise serializers.ValidationError({"code": "Code has expired"})
        if otp.is_verified:
            raise serializers.ValidationError({"code": "Code already used"})

        attrs["user"] = user
        attrs["otp_instance"] = otp
        return attrs

    def create(self, validated_data):
        otp: OTPCode = validated_data["otp_instance"]
        otp.mark_verified()
        expiry = timezone.now() + timedelta(minutes=settings.OTP_VERIFICATION_TOKEN_MINUTES)
        token = OTPVerificationToken.objects.create(user=validated_data["user"], otp=otp, expires_at=expiry)
        return token


class OTPTokenObtainPairSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp_token = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        otp_token_value = attrs.get("otp_token")
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist as exc:
            raise AuthenticationFailed("Invalid credentials") from exc

        token_obj = (
            OTPVerificationToken.objects.filter(user=user, token=otp_token_value)
            .order_by("-created_at")
            .first()
        )
        if not token_obj or token_obj.is_expired:
            raise AuthenticationFailed("Invalid or expired OTP token")

        token_obj.mark_used()
        refresh = RefreshToken.for_user(user)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}


class OTPTokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    otp_token = serializers.CharField()

    def validate(self, attrs):
        otp_token_value = attrs.get("otp_token")
        try:
            refresh = RefreshToken(attrs["refresh"])
        except Exception as exc:  # noqa: BLE001
            raise AuthenticationFailed("Invalid refresh token") from exc

        user_id = refresh.get("user_id")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist as exc:
            raise AuthenticationFailed("User not found") from exc

        token_obj = (
            OTPVerificationToken.objects.filter(user=user, token=otp_token_value)
            .order_by("-created_at")
            .first()
        )
        if not token_obj or token_obj.is_expired:
            raise AuthenticationFailed("Invalid or expired OTP token")

        token_obj.mark_used()
        data = {"access": str(refresh.access_token)}
        if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS"):
            new_refresh = RefreshToken.for_user(user)
            data["refresh"] = str(new_refresh)
        else:
            data["refresh"] = str(refresh)
        return data
