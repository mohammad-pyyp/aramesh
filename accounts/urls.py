# accounts/urls.py
from django.urls import path
from .views import ( login_page, register_page, DashboardView, UserProfileUpdateView, )

app_name = "accounts"

urlpatterns = [
    # Template views
    path("login/", login_page, name="login"),
    path("register/", register_page, name="register"),

    path("dashboard/", DashboardView.as_view(), name="api_dashboard"),
    path("profile/", UserProfileUpdateView.as_view(), name="api_profile"),
]
