from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentCreateSerializer

from django.contrib.auth.decorators import login_required 

# Create your views here.

def welcome_page(request):
    """Render the welcome page"""
    return render(request, 'welcome_page.html')

def coming_soon(request):
    """Render the coming soon page"""
    return render(request, 'comming_soon.html')

@login_required
def user_dashboard(request):
    """Render the user dashboard page"""
    return render(request, 'user_dashboard.html')

def management_appointments(request):
    """Render the management appointments page"""
    return render(request, 'management/management_appointments.html')

# API Views
class AppointmentListView(APIView):
    """Get user's appointments"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        appointments = Appointment.objects.filter(user=request.user)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response({
            "success": True,
            "message": "نوبت‌های کاربر",
            "data": serializer.data
        })

class AppointmentCreateView(APIView):
    """Create a new appointment"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = AppointmentCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            appointment = serializer.save()
            response_serializer = AppointmentSerializer(appointment)
            return Response({
                "success": True,
                "message": "نوبت با موفقیت ثبت شد",
                "data": response_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "خطا در ثبت نوبت",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)