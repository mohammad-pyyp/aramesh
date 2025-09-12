# api/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

PHONE_REGEX = r'^09\d{9}$'  # هم‌خوان با validator مدل User



class SendOTPSerializer(serializers.Serializer):
    phone = serializers.RegexField(regex=PHONE_REGEX, max_length=11, help_text="شماره باید 11 رقم و با 09 شروع شود")

    def validate_phone(self, value):
        return value.strip()


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    phone = serializers.RegexField(regex=PHONE_REGEX, max_length=11)
    otp = serializers.CharField(min_length=6, max_length=6)

    # validate_first_name(){}
    # validate_last_name(){}
    def validate_phone(self, value):
        return value.strip()

    def validate_otp(self, value):
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError("کد OTP باید فقط عدد باشد.")
        if len(value) != 6:
            raise serializers.ValidationError("کد OTP باید دقیقاً 6 رقم باشد.")
        return value


class LoginSerializer(serializers.Serializer):
    phone = serializers.RegexField(regex=PHONE_REGEX, max_length=11)
    otp = serializers.CharField(min_length=6, max_length=6)

    def validate_phone(self, value):
        return value.strip()

    def validate_otp(self, value):
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError("کد OTP باید فقط عدد باشد.")
        if len(value) != 6:
            raise serializers.ValidationError("کد OTP باید دقیقاً 6 رقم باشد.")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'first_name', 'last_name', 'date_joined', 'is_staff')
        read_only_fields = ('id', 'phone', 'date_joined', 'is_staff')




from rest_framework import serializers
from .models import Appointment
from django.contrib.auth import get_user_model

User = get_user_model()

class AppointmentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'user_name', 'service', 'preferred_date', 'preferred_time',
            'notes', 'status', 'confirmed_date', 'confirmed_time', 
            'cancellation_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_name', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['service', 'preferred_date', 'preferred_time', 'notes']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


