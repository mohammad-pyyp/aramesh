# api/urls.py
from django.urls import path
from . import views

app_name = "api"

urlpatterns = [
    path("appointments/", views.UserAppointmentAPIView.as_view(), name="user-appointments"),
]

