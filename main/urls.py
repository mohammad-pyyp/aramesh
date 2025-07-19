from django.urls import path 
from . import views


app_name = 'main'



urlpatterns = [
    path('', views.ReserveTemplateView.as_view() , name="reserve"),
    path('api/submit_reserve_form/', views.submit_reserve_form, name='submit_reserve_form'),
    path('co_so/', views.CommingSoonTemplateView.as_view() , name="co_so")

]




