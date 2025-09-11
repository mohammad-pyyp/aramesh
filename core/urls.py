from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path('', views.welcome_page, name='welcome'),
    path('co-so/', views.coming_soon, name='co_so'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('management-appointments/', views.management_appointments, name='MA'),
]
