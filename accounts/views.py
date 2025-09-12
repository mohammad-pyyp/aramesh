# accounts/views.py
import logging
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import OTP
from .serializers import (SendOTPSerializer, RegisterSerializer, LoginSerializer, ProfileSerializer,)
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.contrib.auth import login , logout
from django.conf import settings
import re

User = get_user_model()
logger = logging.getLogger(__name__)




def normalize_phone(phone: str) -> str:
    """تبدیل ارقام فارسی/عربی و حذف فاصله/خط/نشانه‌ها."""
    if not phone:
        return ''
    mapping = str.maketrans({
        '۰':'0','۱':'1','۲':'2','۳':'3','۴':'4','۵':'5','۶':'6','۷':'7','۸':'8','۹':'9',
        '٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9',
        '‌':'',' ': '','-':''
    })
    p = phone.translate(mapping)
    p = re.sub(r'\D', '', p)  # هرچی غیرعدد هست حذف بشه
    return p



def success_response(message="ok", data=None, status_code=status.HTTP_200_OK):
    return Response({"success": True, "message": message, "data": data or {}}, status=status_code)


def error_response(message, status_code=status.HTTP_400_BAD_REQUEST, data=None):
    return Response({"success": False, "message": message, "data": data or {}}, status=status_code)


def login_page(request):
    """Render the sign-in page"""
    return render(request, 'accounts/login.html')


def register_page(request):
    """Render the sign-up page"""
    return render(request, 'accounts/register.html')


class SendOTPView(APIView):
    """
    POST: {"phone": "09xxxxxxxxx", "mode": "register"|"login"}  # mode optional
    Behavior:
      - applies regen interval and daily limit via OTP.create_for_phone (which raises ValueError -> 429)
      - returns a generic response to avoid user enumeration
    Note: This endpoint DOES create an OTP record (subject to rate limits).
          You must connect SMS gateway in production to actually send `plain_code`.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        # mode intentionally ignored for branching to avoid enumeration; frontend controls flow
        try:
            otp_obj, plain_code = OTP.create_for_phone(phone, ttl_minutes=5, regen_interval_seconds=60)

            print(">>> phone:", phone, "otp_code:", plain_code)  # برای تست
            # send_sms(phone, plain_code)

        except ValueError as e:
            # Rate limiting or regen errors -> 429
            return error_response(str(e), status.HTTP_429_TOO_MANY_REQUESTS)
        except Exception:
            logger.exception("Unexpected error creating OTP for phone=%s", phone)
            return error_response("خطا در سرور هنگام ایجاد OTP", status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Generic response (avoid confirming whether number exists)
        return success_response("اگر شماره معتبر باشد، پیام حاوی کد ارسال خواهد شد.", data={"sent": True}, status_code=status.HTTP_201_CREATED)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        first_name = serializer.validated_data.get('first_name', '')
        last_name = serializer.validated_data.get('last_name', '')
        phone_raw = serializer.validated_data['phone']
        otp_code = serializer.validated_data['otp']

        phone = normalize_phone(phone_raw)

        # find most recent valid OTP(s)
        otp_qs = OTP.objects.filter(phone=phone, is_used=False, expires_at__gt=timezone.now()).order_by('-created_at')
        if not otp_qs.exists():
            return error_response("OTP نامعتبر یا منقضی شده است", status.HTTP_400_BAD_REQUEST)

        otp = otp_qs.first()

        # Atomic: چک وجود کاربر، مصرف OTP و ایجاد کاربر را در یک تراکنش انجام می‌دهیم
        try:
            with transaction.atomic():
                # اگر کاربر از قبل وجود دارد، همه OTPهای فعال را غیرفعال کن و خطا برگردان
                if User.objects.filter(phone=phone).exists():
                    OTP.objects.filter(phone=phone, is_used=False).update(is_used=True)
                    return error_response("شماره قبلاً ثبت شده است. از ورود استفاده کنید.", status.HTTP_400_BAD_REQUEST)

                # حالا کد را مصرف (verify + mark used) می‌کنیم
                ok, reason = otp.consume(otp_code)
                if not ok:
                    if reason == "max_attempts":
                        return error_response("تعداد تلاش‌ها بیش از حد مجاز شده است.", status.HTTP_400_BAD_REQUEST)
                    return error_response("OTP نامعتبر یا منقضی شده است", status.HTTP_400_BAD_REQUEST)

                # ایجاد کاربر (اگر همزمان کسی دیگر ایجاد کرد، IntegrityError را هندل می‌کنیم)
                user = User.objects.create_user(phone=phone, first_name=first_name, last_name=last_name)

        except IntegrityError:
            logger.warning("IntegrityError on creating user for phone=%s", phone)
            # اگر اینجا بیایم، احتمالا کاربر در بازه‌ی بین چک و create ساخته شده؛ پیام مناسب بده
            return error_response("خطا در ثبت‌نام — شماره قبلاً ثبت شده است.", status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("Unexpected error while creating user for phone=%s", phone)
            return error_response("خطا در سرور هنگام ثبت‌نام", status.HTTP_500_INTERNAL_SERVER_ERROR)

        # لاگین: مشخص کردن backend توصیه می‌شود
        try:
            login(request, user)
        except Exception:
            # حتی اگر login شدنی نبود، کاربر ساخته شده؛ ولی بهتر لاگ کنیم و پاسخ مناسب برگردانیم
            logger.exception("Failed to login user after registration phone=%s", phone)

        return success_response("ثبت‌نام موفق", data={
            "user": {
                "id": user.id,
                "phone": user.phone,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        }, status_code=status.HTTP_201_CREATED)

# class RegisterView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         print(serializer.validated_data)
#         first_name = serializer.validated_data.get('first_name', '')
#         last_name = serializer.validated_data.get('last_name', '')
#         phone = serializer.validated_data['phone']
#         otp_code = serializer.validated_data['otp']

#         # find most recent valid OTP(s)
#         otp_qs = OTP.objects.filter(phone=phone, is_used=False, expires_at__gt=timezone.now()).order_by('-created_at')
#         if not otp_qs.exists():
#             return error_response("OTP نامعتبر یا منقضی شده است", status.HTTP_400_BAD_REQUEST)

#         otp = otp_qs.first()
#         ok, reason = otp.consume(otp_code)
#         if not ok:
#             if reason == "max_attempts":
#                 return error_response("تعداد تلاش‌ها بیش از حد مجاز شده است.", status.HTTP_400_BAD_REQUEST)
#             return error_response("OTP نامعتبر یا منقضی شده است", status.HTTP_400_BAD_REQUEST)

#         # Atomic user creation with race protection
#         try:
#             with transaction.atomic():
#                 if User.objects.filter(phone=phone).exists():
#                     OTP.objects.filter(phone=phone, is_used=False).update(is_used=True)
#                     return error_response("شماره قبلاً ثبت شده است. از ورود استفاده کنید.", status.HTTP_400_BAD_REQUEST)

#                 user = User.objects.create_user(phone=phone, first_name=first_name, last_name=last_name)
#         except IntegrityError:
#             logger.warning("IntegrityError on creating user for phone=%s", phone)
#             return error_response("خطا در ثبت‌نام — شماره قبلاً ثبت شده است.", status.HTTP_400_BAD_REQUEST)
#         except Exception:
#             logger.exception("Unexpected error while creating user for phone=%s", phone)
#             return error_response("خطا در سرور هنگام ثبت‌نام", status.HTTP_500_INTERNAL_SERVER_ERROR)

#         login(request, user)  # ایجاد سشن
#         # TODO Redirect user to dashboard (OR) Redirect admin to management page
#         return success_response("ثبت‌نام موفق", data={
#             "user": {
#                 "id": user.id,
#                 "phone": user.phone,
#                 "first_name": user.first_name,
#                 "last_name": user.last_name,
#             }
#         }, status_code=status.HTTP_201_CREATED)



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        otp_code = serializer.validated_data['otp']

        otp_qs = OTP.objects.filter(phone=phone, is_used=False, expires_at__gt=timezone.now()).order_by('-created_at')
        if not otp_qs.exists():
            return error_response("OTP نامعتبر یا منقضی شده است", status.HTTP_400_BAD_REQUEST)

        otp = otp_qs.first()
        ok, reason = otp.consume(otp_code)
        if not ok:
            if reason == "max_attempts":
                return error_response("تعداد تلاش‌ها بیش از حد مجاز شده است.", status.HTTP_400_BAD_REQUEST)
            return error_response("OTP نامعتبر یا منقضی شده است", status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            # safer message: do not auto-create user here
            return error_response("کاربری با این شماره وجود ندارد. ابتدا ثبت‌نام کنید.", status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return error_response("حساب کاربری غیرفعال است.", status.HTTP_403_FORBIDDEN)

        # پس از اعتبارسنجی OTP و گرفتن user
        login(request, user)
        # TODO Redirect user to dashboard (OR) Redirect admin to management page
        return success_response("ورود موفق", data={
            "user": {
                "id": user.id,
                "phone": user.phone,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        })


class DashboardView(APIView):
    """
    GET: Authorization: Bearer <access_token>

    data:{
        user : { . . . }
        aponents : { . . . }
    }
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return success_response("پروفایل کاربر", data=serializer.data)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)  # پاک کردن سشن
        return success_response("خروج موفقیت‌آمیز")



class UserProfileUpdateView(APIView):
    """Update user profile"""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return success_response("پروفایل با موفقیت به‌روزرسانی شد", data=serializer.data)
        
        return error_response("داده‌های نامعتبر", data=serializer.errors)



