from django.db import models
from django.contrib.auth.models import PermissionsMixin , AbstractUser
from  django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import RegexValidator
from .managers import UserManager
# from datetime import timedelta
# import secrets
# import string
import logging
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.db import models  # , transaction
# from django.utils import timezone
from django.core.cache import cache


logger = logging.getLogger(__name__)


class User(AbstractUser, PermissionsMixin):
    email = None
    username = None
    # username_validator = ASCIIUsernameValidator
    # username = models.CharField(
    #     ("username"),
    #     max_length=250,
    #     unique=True,
    #     help_text= (
    #     "ضروری. حداکثر ۲۵۰ کاراکتر. فقط شامل حروف انگلیسی (a-z, A-Z)، "
    #     "اعداد (0-9) و کاراکترهای @ . + - _ مجاز است."
    #     ),
    #     validators=[username_validator],
    #     error_messages={
    #         "unique": ("این نام کاربری قبلاً استفاده شده است."),
    #         "blank": ("لطفاً یک نام کاربری وارد کنید."),
    #         "invalid": ("نام کاربری وارد شده نامعتبر است."),
    #     },
    # )

    persian_arabic_letters_validator = RegexValidator(
        regex=r'^[آ-یءئ\s‌يك]+$',
        message= ("این فیلد فقط می‌تواند شامل حروف فارسی یا عربی باشد."),
        code="invalid_name"
    )
    
    first_name = models.CharField(
        ("نام"),
        max_length=250,
        validators=[persian_arabic_letters_validator],
        help_text=("حداکثر ۲۵۰ کاراکتر. فقط حروف فارسی مجاز است."),
        error_messages={
            "blank": ("لطفاً نام را وارد کنید."),
            "max_length": ("نام نمی‌تواند بیشتر از ۲۵۰ کاراکتر باشد."),
            "invalid_name": ("نام فقط باید شامل حروف فارسی باشد."),
        },
    )

    last_name = models.CharField(
        ("نام خانوادگی"),
        max_length=250,
        validators=[persian_arabic_letters_validator],
        help_text= ("حداکثر ۲۵۰ کاراکتر. فقط حروف فارسی مجاز است."),
        error_messages={
            "blank": ("لطفاً نام خانوادگی را وارد کنید."),
            "max_length": ("نام خانوادگی نمی‌تواند بیشتر از ۲۵۰ کاراکتر باشد."),
            "invalid_name": ("نام خانوادگی فقط باید شامل حروف فارسی باشد."),
        },
    )

    phone = models.CharField(("شماره تلفن"),max_length=11 ,unique=True ,
        validators=[
            RegexValidator(
                regex=r'^09\d{9}$',
                message="شماره تلفن باید با 09 شروع شده و 11 رقم باشد.",
                code="invalid_phone_number"
            )
        ],
        error_messages={
            "unique": "این شماره تلفن قبلاً استفاده شده است.",
        }
    )
    
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    EMAIL_FIELD = None
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در حال بررسی'),
        ('approved', 'تایید شد'),
        ('canceled', 'لغو شد'),
    ]

    SLOTS_CHOICES = [
        ( '8_00'  , '08:00' ),
        ( '8_30'  , '08:30' ),
        ( '9_00'  , '09:00' ),
        ( '9_30'  , '09:30' ),
        ( '10_00' , '10:00' ),
        ( '10_30' , '10:30' ),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    slot = models.CharField(max_length=6, choices=SLOTS_CHOICES, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.status}"







# ---------- OTP ----------
# class OTP(models.Model):
#     """
#     OTP model:
#       - stores hashed code (make_password)
#       - supports per-phone daily limit via cache
#       - supports regen interval via cache
#       - consume() is atomic and locks all active OTP rows for the phone to avoid races
#     Note: This implementation assumes incoming `phone` is already normalized/correct.
#     """

#     phone = models.CharField(max_length=20, db_index=True)
#     code_hash = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField()
#     is_used = models.BooleanField(default=False)
#     attempts = models.PositiveSmallIntegerField(default=0)

#     MAX_ATTEMPTS = getattr(settings, 'OTP_MAX_ATTEMPTS', 5)
#     DAILY_LIMIT = getattr(settings, 'OTP_DAILY_LIMIT', 10)

#     class Meta:
#         ordering = ['-created_at']

#     @classmethod
#     def generate_code(cls, length: int = 6) -> str:
#         """Generate numeric OTP code."""
#         return ''.join(secrets.choice(string.digits) for _ in range(length))

#     @classmethod
#     def _seconds_until_midnight(cls) -> int:
#         now = timezone.now()
#         tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
#         return int((tomorrow - now).total_seconds())

#     @classmethod
#     def create_for_phone(cls, phone: str, ttl_minutes: int = 5, regen_interval_seconds: int = 60):
#         """
#         Create OTP for phone with:
#           - regen short lock (regen_interval_seconds) using cache.add (non-blocking)
#           - daily limit using cache counter (attempt atomic incr when available)
#         Returns: (otp_instance, plain_code)
#         Raises ValueError on rate limits (caller should map to HTTP 429).
#         """
#         phone = phone.strip()
#         now = timezone.now()

#         regen_cache_key = f"otp:locked:{phone}"
#         # cache.add returns False if key already exists -> locked
#         locked = not cache.add(regen_cache_key, "1", timeout=regen_interval_seconds)
#         if locked:
#             raise ValueError("درخواست خیلی سریع تکرار شد. کمی بعد دوباره تلاش کنید.")  # client 429

#         date_key = now.strftime("%Y-%m-%d")
#         daily_cache_key = f"otp:daily:{phone}:{date_key}"
#         daily_count = cache.get(daily_cache_key, 0)
#         if daily_count >= cls.DAILY_LIMIT:
#             raise ValueError("تعداد درخواست‌های روزانه برای این شماره به حد مجاز رسیده است.")  # client 429

#         # produce code and save hashed
#         code = cls.generate_code()
#         otp = cls(
#             phone=phone,
#             code_hash=make_password(code),
#             expires_at=now + timedelta(minutes=ttl_minutes)
#         )
#         otp.save()

#         # increment daily counter: try atomic incr first (Redis), fallback gracefully
#         try:
#             # If key doesn't exist, incr may raise ValueError -> set below
#             cache.incr(daily_cache_key)
#         except ValueError:
#             # key not exists
#             cache.set(daily_cache_key, 1, timeout=cls._seconds_until_midnight())
#         except Exception:
#             # backend may not implement incr (or other error), fallback to read/set
#             try:
#                 current = cache.get(daily_cache_key, 0)
#                 cache.set(daily_cache_key, current + 1, timeout=cls._seconds_until_midnight())
#             except Exception:
#                 logger.exception("Failed to update daily OTP counter for phone=%s", phone)

#         logger.debug("OTP created for phone=%s id=%s (do NOT log code in production)", phone, otp.id)
#         return otp, code

#     def is_valid(self) -> bool:
#         return (not self.is_used) and (self.expires_at > timezone.now()) and (self.attempts < self.MAX_ATTEMPTS)

#     def consume(self, code: str):
#         """
#         Atomically verify code, mark as used and invalidate other active OTPs for same phone.
#         Returns: (True, None) on success
#                  (False, reason) where reason in {"expired_or_used", "max_attempts", "invalid"}
#         """
#         # Lock all active OTP rows for this phone to avoid race conditions
#         with transaction.atomic():
#             active_qs = OTP.objects.select_for_update().filter(phone=self.phone, is_used=False)
#             try:
#                 otp = active_qs.get(pk=self.pk)
#             except OTP.DoesNotExist:
#                 # either already used/expired or caller has stale instance
#                 return False, "expired_or_used"

#             now = timezone.now()
#             if otp.is_used or otp.expires_at <= now:
#                 return False, "expired_or_used"

#             if otp.attempts >= otp.MAX_ATTEMPTS:
#                 return False, "max_attempts"

#             # verify
#             if check_password(code, otp.code_hash):
#                 otp.is_used = True
#                 otp.save(update_fields=['is_used'])
#                 # mark other active OTPs for same phone as used (we already locked them)
#                 active_qs.exclude(pk=otp.pk).update(is_used=True)
#                 return True, None
#             else:
#                 otp.attempts += 1
#                 otp.save(update_fields=['attempts'])
#                 if otp.attempts >= otp.MAX_ATTEMPTS:
#                     return False, "max_attempts"
#                 return False, "invalid"

#     def mark_used(self):
#         if not self.is_used:
#             self.is_used = True
#             self.save(update_fields=['is_used'])


