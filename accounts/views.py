# api/views.py
import logging
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .models import OTP
from .serializers import (
    SendOTPSerializer, RegisterSerializer, LoginSerializer, ProfileSerializer,
    TokenRefreshSerializer, LogoutSerializer
)
from django.contrib.auth import get_user_model
from django.shortcuts import render

User = get_user_model()
logger = logging.getLogger(__name__)


def success_response(message="ok", data=None, status_code=status.HTTP_200_OK):
    return Response({"success": True, "message": message, "data": data or {}}, status=status_code)


def error_response(message, status_code=status.HTTP_400_BAD_REQUEST, data=None):
    return Response({"success": False, "message": message, "data": data or {}}, status=status_code)


def sing_in_page(request):
    """Render the sign-in page"""
    return render(request, 'accounts/sing_in.html')


def sing_up_page(request):
    """Render the sign-up page"""
    return render(request, 'accounts/sing_up.html')


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
            # TODO: Hook into actual SMS gateway here:
            # send_sms(phone, plain_code)
            print(">>> phone:", phone, "otp_code:", plain_code)  # برای تست
            # logger.debug("phone=%s, otp=%s", phone, plain_code)  # در لاگ
            # logger.info("OTP created for phone=%s (otp_id=%s). SMS should be sent via gateway.", phone, otp_obj.id)
            # logger.debug("DEV ONLY: OTP for phone=%s code=%s", phone, plain_code)
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

        phone = serializer.validated_data['phone']
        otp_code = serializer.validated_data['otp']
        first_name = serializer.validated_data.get('first_name', '')
        last_name = serializer.validated_data.get('last_name', '')

        # find most recent valid OTP(s)
        otp_qs = OTP.objects.filter(phone=phone, is_used=False, expires_at__gt=timezone.now()).order_by('-created_at')
        if not otp_qs.exists():
            return error_response("OTP نامعتبر یا منقضی شده است", status.HTTP_400_BAD_REQUEST)

        otp = otp_qs.first()
        ok, reason = otp.consume(otp_code)
        if not ok:
            if reason == "max_attempts":
                return error_response("تعداد تلاش‌ها بیش از حد مجاز شده است.", status.HTTP_400_BAD_REQUEST)
            return error_response("OTP نامعتبر یا منقضی شده است", status.HTTP_400_BAD_REQUEST)

        # Atomic user creation with race protection
        try:
            with transaction.atomic():
                if User.objects.filter(phone=phone).exists():
                    OTP.objects.filter(phone=phone, is_used=False).update(is_used=True)
                    return error_response("شماره قبلاً ثبت شده است. از ورود استفاده کنید.", status.HTTP_400_BAD_REQUEST)

                user = User.objects.create_user(phone=phone, first_name=first_name, last_name=last_name)
        except IntegrityError:
            logger.warning("IntegrityError on creating user for phone=%s", phone)
            return error_response("خطا در ثبت‌نام — شماره قبلاً ثبت شده است.", status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("Unexpected error while creating user for phone=%s", phone)
            return error_response("خطا در سرور هنگام ثبت‌نام", status.HTTP_500_INTERNAL_SERVER_ERROR)

        refresh = RefreshToken.for_user(user)
        return success_response("ثبت‌نام موفق", data={
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status_code=status.HTTP_201_CREATED)


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

        refresh = RefreshToken.for_user(user)
        return success_response("ورود موفق", data={
            "refresh": str(refresh),
            "access": str(refresh.access_token),
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


class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh view with enhanced error handling"""
    serializer_class = TokenRefreshSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return error_response("توکن نامعتبر یا منقضی شده است", status.HTTP_401_UNAUTHORIZED)
        except InvalidToken as e:
            return error_response("توکن نامعتبر است", status.HTTP_401_UNAUTHORIZED)
        
        return success_response("توکن با موفقیت تازه‌سازی شد", data=serializer.validated_data)


class LogoutView(APIView):
    """Logout view that blacklists the refresh token"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            refresh_token = serializer.validated_data['refresh']
            refresh_token.blacklist()
            
            return success_response("خروج موفقیت‌آمیز", status_code=status.HTTP_200_OK)
            
        except TokenError as e:
            return error_response("توکن نامعتبر است", status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Error during logout for user %s", request.user.id)
            return error_response("خطا در خروج از سیستم", status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutAllView(APIView):
    """Logout from all devices by blacklisting all user tokens"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Get all outstanding refresh tokens for the user
            from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
            
            tokens = OutstandingToken.objects.filter(user=request.user)
            for token in tokens:
                try:
                    refresh_token = RefreshToken(token.token)
                    refresh_token.blacklist()
                except TokenError:
                    # Token might already be blacklisted or invalid
                    pass
            
            return success_response("خروج از تمام دستگاه‌ها موفقیت‌آمیز", status_code=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception("Error during logout all for user %s", request.user.id)
            return error_response("خطا در خروج از تمام دستگاه‌ها", status.HTTP_500_INTERNAL_SERVER_ERROR)


class TokenVerifyView(APIView):
    """Verify if a token is valid"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        token = request.data.get('token')
        
        if not token:
            return error_response("توکن ارائه نشده است", status.HTTP_400_BAD_REQUEST)
        
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            
            # Get user from token
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            
            return success_response("توکن معتبر است", data={
                'valid': True,
                'user': {
                    'id': user.id,
                    'phone': user.phone,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
            
        except TokenError:
            return error_response("توکن نامعتبر است", status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return error_response("کاربر یافت نشد", status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.exception("Error verifying token")
            return error_response("خطا در بررسی توکن", status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileUpdateView(APIView):
    """Update user profile"""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return success_response("پروفایل با موفقیت به‌روزرسانی شد", data=serializer.data)
        
        return error_response("داده‌های نامعتبر", data=serializer.errors)



