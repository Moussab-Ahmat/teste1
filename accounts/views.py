from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    OTPRequestSerializer,
    OTPTokenObtainPairSerializer,
    OTPTokenRefreshSerializer,
    OTPVerifySerializer,
)


class OTPRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = OTPRequestSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            otp = serializer.save()
        except serializers.ValidationError as exc:
            status_code = status.HTTP_400_BAD_REQUEST
            error_codes = exc.get_codes() if hasattr(exc, "get_codes") else None
            if error_codes and "rate_limit" in str(error_codes):
                status_code = status.HTTP_429_TOO_MANY_REQUESTS
            return Response(exc.detail, status=status_code)

        return Response(
            {"detail": "OTP sent", "expires_at": otp.expires_at}, status=status.HTTP_201_CREATED
        )


class OTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        return Response({"otp_token": token.token, "expires_at": token.expires_at}, status=status.HTTP_200_OK)


class OTPTokenObtainPairView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = OTPTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class OTPTokenRefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = OTPTokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
