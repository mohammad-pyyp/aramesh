from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("phone",)
    list_display = ("phone", "first_name", "last_name", "is_staff", "is_active")
    search_fields = ("phone", "first_name", "last_name")

    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        (_("اطلاعات شخصی"), {"fields": ("first_name", "last_name")}),
        (_("دسترسی‌ها"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("تاریخ‌ها"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone", "password1", "password2", "is_active", "is_staff", "is_superuser"),
        }),
    )
