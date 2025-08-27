from django.contrib.auth.backends import ModelBackend
from .models import User


class PhoneBackend(ModelBackend):
    def authenticate(self, request, phone=None, password=None, **kwargs):
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None

        # اگر کاربر ادمین است → باید پسورد چک شود
        if user.is_staff or user.is_superuser:
            if password and user.check_password(password):
                return user
            return None

        # اگر کاربر معمولی است → ورود فقط با شماره تلفن
        if not user.is_staff and not user.is_superuser:
            return user

        return None
