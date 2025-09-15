# pages/urls.py
from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.HomePage.as_view(), name="home"),
    path("cooming_soon/", views.CommingSoon.as_view(), name="comming_soon"),
    path("login/", views.LoginPage.as_view(), name="login"),
    path("register/", views.RegisterPage.as_view(), name="register"),
    path("dashboard/", views.DashboardPage.as_view(), name="dashboard"),
    path("logout/", views.logout_view , name="logout"),

]
