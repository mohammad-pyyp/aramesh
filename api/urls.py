# api/urls.py
from django.urls import path
from .views import (
                    SendOTPView , RegisterView, LoginView , DashboardView , UserProfileUpdateView ,
                    AppointmentListView , AppointmentCreateView ,
            )

app_name = "api"

urlpatterns = [
    # User profile
    # path("dashboard/", DashboardView.as_view(), name="dashboard"),
    # path("profile/", UserProfileUpdateView.as_view(), name="profile_update"),
    
    # API views
    path("send-otp/", SendOTPView.as_view(), name="send_otp"),
    path("register/", RegisterView.as_view(), name="api_register"),
    path("login/", LoginView.as_view(), name="api_login"),

    # Appointments
    path("appointments/", AppointmentListView.as_view(), name="appointments_list"),
    path("appointments/create/", AppointmentCreateView.as_view(), name="appointments_create"),
]

