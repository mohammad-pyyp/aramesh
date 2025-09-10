# accounts/urls.py
from django.urls import path
from .views import sing_in_page, sing_up_page

app_name = "accounts"

urlpatterns = [
    # Template views
    path("sing-in/", sing_in_page, name="sing_in"),
    path("sing-up/", sing_up_page, name="sing_up"),
]


