# api/urls.py
from django.urls import path
from accounts.views import SendOTPView, RegisterView, LoginView, DashboardView, LogoutView, UserProfileUpdateView
from core.views import AppointmentListView, AppointmentCreateView

app_name = "api"

urlpatterns = [
    # User profile
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("profile/", UserProfileUpdateView.as_view(), name="profile_update"),
    
    # API views
    path("send-otp/", SendOTPView.as_view(), name="send_otp"),
    path("register/", RegisterView.as_view(), name="api_register"),
    path("login/", LoginView.as_view(), name="api_login"),
    path("logout/", LogoutView.as_view(), name="api_logout"),

    # Appointments
    path("appointments/", AppointmentListView.as_view(), name="appointments_list"),
    path("appointments/create/", AppointmentCreateView.as_view(), name="appointments_create"),
]