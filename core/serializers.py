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
