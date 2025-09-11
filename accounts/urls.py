# accounts/urls.py
from django.urls import path
from .views import login_page, register_page

app_name = "accounts"

urlpatterns = [
    # Template views
    path("login/", login_page, name="login"),
    path("register/", register_page, name="register"),
]


