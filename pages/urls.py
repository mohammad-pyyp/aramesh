# pages/urls.py
from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.welcome_page , name="welcome"),
    path("login/", views.login_page, name="login"),
    path("register/",views.register_page, name="register"),
    path("logout/", views.logout_view , name="logout"),
]
    
