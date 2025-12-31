from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import OTPSendLog, OTPCode, OTPVerificationToken, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("phone_number", "password", "full_name", "role")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "role", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )
    list_display = ("phone_number", "role", "is_staff", "is_active")
    search_fields = ("phone_number", "full_name")
    ordering = ("phone_number",)
    filter_horizontal = ("groups", "user_permissions")


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "is_verified", "expires_at", "created_at")
    list_filter = ("is_verified", "created_at")
    search_fields = ("user__phone_number", "code")


@admin.register(OTPVerificationToken)
class OTPVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "expires_at", "used_at")
    list_filter = ("used_at",)
    search_fields = ("token", "user__phone_number")


@admin.register(OTPSendLog)
class OTPSendLogAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "message", "created_at")
    search_fields = ("phone_number", "message")
