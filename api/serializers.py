# api/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Appointment


# سریالایزر کاربر
class AppointmentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id", "status", "status_display", "slot", "date", "cancellation_reason"
        ]
        read_only_fields = ["status", "slot", "date", "cancellation_reason"]


class AdminAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"





# class SendOTPSerializer(serializers.Serializer):
#     phone = serializers.RegexField(regex=PHONE_REGEX, max_length=11, help_text="شماره باید 11 رقم و با 09 شروع شود")

#     def validate_phone(self, value):
#         return value.strip()


# class RegisterSerializer(serializers.Serializer):
#     first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
#     last_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
#     phone = serializers.RegexField(regex=PHONE_REGEX, max_length=11)
#     otp = serializers.CharField(min_length=6, max_length=6)

#     # validate_first_name(){}
#     # validate_last_name(){}
#     def validate_phone(self, value):
#         return value.strip()

#     def validate_otp(self, value):
#         value = value.strip()
#         if not value.isdigit():
#             raise serializers.ValidationError("کد OTP باید فقط عدد باشد.")
#         if len(value) != 6:
#             raise serializers.ValidationError("کد OTP باید دقیقاً 6 رقم باشد.")
#         return value


# class LoginSerializer(serializers.Serializer):
#     phone = serializers.RegexField(regex=PHONE_REGEX, max_length=11)
#     otp = serializers.CharField(min_length=6, max_length=6)

#     def validate_phone(self, value):
#         return value.strip()

#     def validate_otp(self, value):
#         value = value.strip()
#         if not value.isdigit():
#             raise serializers.ValidationError("کد OTP باید فقط عدد باشد.")
#         if len(value) != 6:
#             raise serializers.ValidationError("کد OTP باید دقیقاً 6 رقم باشد.")
#         return value


# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'phone', 'first_name', 'last_name', 'date_joined', 'is_staff')
#         read_only_fields = ('id', 'phone', 'date_joined', 'is_staff')



