from django.urls import path 
from . import views


app_name = 'main'

urlpatterns = [
    path('', views.WelcomePage.as_view(),name="welcome_page" ),
    path('user_dashboard/', views.UserDashboardTemplateView.as_view(), name="user_dashboard" ),
    path('comming_soon/', views.CommingSoonTemplateView.as_view(), name="co_so" ),
    path('ma/', views.ManagementAappointmentsTemplateView.as_view(), name="MA" ),
    

]




