import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


PHONE_PREFIX = "+235"
PHONE_VALIDATOR = RegexValidator(
    regex=r"^\+235\d{8}$", message="Phone number must start with +235 followed by 8 digits."
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone_number: str, password: str | None, **extra_fields):
        if not phone_number:
            raise ValueError("The phone number must be set")
        if not phone_number.startswith(PHONE_PREFIX):
            raise ValueError("Phone number must start with +235")
        phone_number = self.normalize_email(phone_number)
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, phone_number: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Roles.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        ADMIN = "ADMIN", "Admin"
        WAREHOUSE = "WAREHOUSE", "Warehouse"
        COURIER = "COURIER", "Courier"

    phone_number = models.CharField(
        max_length=20, unique=True, validators=[PHONE_VALIDATOR], help_text="Unique phone number with +235 prefix."
    )
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CUSTOMER)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS: list[str] = []

    def __str__(self) -> str:
        return self.phone_number


class OTPCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="otp_codes", on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def mark_verified(self):
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save(update_fields=["is_verified", "verified_at"])

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at


class OTPVerificationToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="otp_tokens", on_delete=models.CASCADE)
    otp = models.ForeignKey(OTPCode, related_name="verification_tokens", on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    def mark_used(self):
        if not self.used_at:
            self.used_at = timezone.now()
            self.save(update_fields=["used_at"])


class OTPSendLog(models.Model):
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"OTP sent to {self.phone_number} at {self.created_at.isoformat()}"
