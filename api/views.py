# accounts/views.py
import logging
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from .serializers import AppointmentSerializer

from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.contrib.auth import login
from .models import Appointment


User = get_user_model()
logger = logging.getLogger(__name__)



def success_response(message="ok", data=None, status_code=status.HTTP_200_OK):
    return Response({"success": True, "message": message, "data": data or {}}, status=status_code)


def error_response(message, status_code=status.HTTP_400_BAD_REQUEST, data=None):
    return Response({"success": False, "message": message, "data": data or {}}, status=status_code)



class UserAppointmentAPIView(ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)







# class RegisterView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         first_name = serializer.validated_data.get('first_name', '')
#         last_name = serializer.validated_data.get('last_name', '')
#         phone = serializer.validated_data['phone']
#         otp_code = serializer.validated_data['otp']

#         # find most recent valid OTP(s)
#         otp_qs = OTP.objects.filter(phone=phone, is_used=False, expires_at__gt=timezone.now()).order_by('-created_at')
#         if not otp_qs.exists():
#             return error_response("OTP نامعتبر یا منقضی شده است", status.HTTP_400_BAD_REQUEST)

#         otp = otp_qs.first()

#         # Atomic: چک وجود کاربر، مصرف OTP و ایجاد کاربر را در یک تراکنش انجام می‌دهیم
#         try:
#             with transaction.atomic():
#                 # اگر کاربر از قبل وجود دارد، همه OTPهای فعال را غیرفعال کن و خطا برگردان
#                 if User.objects.filter(phone=phone).exists():
#                     OTP.objects.filter(phone=phone, is_used=False).update(is_used=True)
#                     return error_response("شماره قبلاً ثبت شده است. از ورود استفاده کنید.", status.HTTP_400_BAD_REQUEST)

#                 # حالا کد را مصرف (verify + mark used) می‌کنیم
#                 ok, reason = otp.consume(otp_code)
#                 if not ok:
#                     if reason == "max_attempts":
#                         return error_response("تعداد تلاش‌ها بیش از حد مجاز شده است.", status.HTTP_400_BAD_REQUEST)
#                     return error_response("OTP نامعتبر یا منقضی شده است", status.HTTP_400_BAD_REQUEST)

#                 # ایجاد کاربر (اگر همزمان کسی دیگر ایجاد کرد، IntegrityError را هندل می‌کنیم)
#                 user = User.objects.create_user(phone=phone, first_name=first_name, last_name=last_name)

#         except IntegrityError:
#             logger.warning("IntegrityError on creating user for phone=%s", phone)
#             # اگر اینجا بیایم، احتمالا کاربر در بازه‌ی بین چک و create ساخته شده؛ پیام مناسب بده
#             return error_response("خطا در ثبت‌نام — شماره قبلاً ثبت شده است.", status.HTTP_400_BAD_REQUEST)
#         except Exception:
#             logger.exception("Unexpected error while creating user for phone=%s", phone)
#             return error_response("خطا در سرور هنگام ثبت‌نام", status.HTTP_500_INTERNAL_SERVER_ERROR)

#         # لاگین: مشخص کردن backend توصیه می‌شود
#         try:
#             login(request, user)
#         except Exception:
#             # حتی اگر login شدنی نبود، کاربر ساخته شده؛ ولی بهتر لاگ کنیم و پاسخ مناسب برگردانیم
#             logger.exception("Failed to login user after registration phone=%s", phone)

#         return success_response("ثبت‌نام موفق", data={
#             "user": {
#                 "id": user.id,
#                 "phone": user.phone,
#                 "first_name": user.first_name,
#                 "last_name": user.last_name,
#             }
#         }, status_code=status.HTTP_201_CREATED)



# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         phone = serializer.validated_data['phone']
#         otp_code = serializer.validated_data['otp']

#         otp_qs = OTP.objects.filter(phone=phone, is_used=False, expires_at__gt=timezone.now()).order_by('-created_at')
#         if not otp_qs.exists():
#             return error_response("OTP نامعتبر یا منقضی شده است", status.HTTP_400_BAD_REQUEST)

#         otp = otp_qs.first()
#         ok, reason = otp.consume(otp_code)
#         if not ok:
#             if reason == "max_attempts":
#                 return error_response("تعداد تلاش‌ها بیش از حد مجاز شده است.", status.HTTP_400_BAD_REQUEST)
#             return error_response("OTP نامعتبر یا منقضی شده است", status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.get(phone=phone)
#         except User.DoesNotExist:
#             # safer message: do not auto-create user here
#             return error_response("کاربری با این شماره وجود ندارد. ابتدا ثبت‌نام کنید.", status.HTTP_400_BAD_REQUEST)

#         if not user.is_active:
#             return error_response("حساب کاربری غیرفعال است.", status.HTTP_403_FORBIDDEN)

#         # پس از اعتبارسنجی OTP و گرفتن user
#         login(request, user)
#         # TODO Redirect user to dashboard (OR) Redirect admin to management page
#         return success_response("ورود موفق", data={
#             "user": {
#                 "id": user.id,
#                 "phone": user.phone,
#                 "first_name": user.first_name,
#                 "last_name": user.last_name,
#             }
#         })


# class DashboardView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         serializer = ProfileSerializer(request.user)
#         return success_response("پروفایل کاربر", data=serializer.data)


# class UserProfileUpdateView(APIView):
#     """Update user profile"""
#     permission_classes = [IsAuthenticated]
    
#     def patch(self, request):
#         serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        
#         if serializer.is_valid():
#             serializer.save()
#             return success_response("پروفایل با موفقیت به‌روزرسانی شد", data=serializer.data)
        
#         return error_response("داده‌های نامعتبر", data=serializer.errors)







