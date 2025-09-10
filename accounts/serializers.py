# api/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import OTP
import re

User = get_user_model()

PHONE_REGEX = r'^09\d{9}$'  # هم‌خوان با validator مدل User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer with additional user data"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['phone'] = user.phone
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_staff'] = user.is_staff
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user data to response
        data['user'] = {
            'id': self.user.id,
            'phone': self.user.phone,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_staff': self.user.is_staff,
            'date_joined': self.user.date_joined,
        }
        
        return data


class SendOTPSerializer(serializers.Serializer):
    phone = serializers.RegexField(regex=PHONE_REGEX, max_length=11, help_text="شماره باید 11 رقم و با 09 شروع شود")
    mode = serializers.ChoiceField(choices=(('register', 'register'), ('login', 'login')),
                                   default='register', required=False)

    def validate_phone(self, value):
        return value.strip()


class RegisterSerializer(serializers.Serializer):
    phone = serializers.RegexField(regex=PHONE_REGEX, max_length=11)
    first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
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


class TokenRefreshSerializer(serializers.Serializer):
    """Custom refresh token serializer"""
    refresh = serializers.CharField()
    
    def validate(self, attrs):
        refresh = attrs['refresh']
        
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            token = RefreshToken(refresh)
            attrs['refresh'] = token
        except Exception:
            raise serializers.ValidationError("توکن نامعتبر است.")
        
        return attrs


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout functionality"""
    refresh = serializers.CharField()
    
    def validate(self, attrs):
        refresh = attrs['refresh']
        
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            token = RefreshToken(refresh)
            attrs['refresh'] = token
        except Exception:
            raise serializers.ValidationError("توکن نامعتبر است.")
        
        return attrs
