# pages/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import UserLoginForm


app_name = "pages"



urlpatterns = [
    path("", views.HomePage.as_view(), name="home"),
    path("cooming_soon/", views.CommingSoonPage.as_view(), name="comming_soon"),

    path("register/", views.RegistrationView.as_view(), name="register"),
    path('login/', auth_views.LoginView.as_view(
        template_name='pages/public/user/auth/login.html',
        authentication_form=UserLoginForm,
        redirect_authenticated_user=True # Redirect if user is already logged in
    ), name='login'),


    path("login/", views.LoginPage.as_view(), name="login"),
    path("dashboard/", views.DashboardPage.as_view(), name="dashboard"),
    path("logout/", views.logout_view , name="logout"),

]


