# api/urls.py
from django.urls import path
from accounts.views import (
    SendOTPView, RegisterView, LoginView, DashboardView,
    CustomTokenRefreshView, LogoutView, LogoutAllView, 
    TokenVerifyView, UserProfileUpdateView
)

app_name = "api"

urlpatterns = [
    # Authentication endpoints
    path("send-otp/", SendOTPView.as_view(), name="send_otp"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    
    # JWT token management
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("logout-all/", LogoutAllView.as_view(), name="logout_all"),
    
    # User profile
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("profile/", UserProfileUpdateView.as_view(), name="profile_update"),
]