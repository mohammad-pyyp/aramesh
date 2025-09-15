from django.contrib.auth.decorators import login_required 
from django.shortcuts import  redirect
from django.views.generic import TemplateView as PageView
from django.contrib.auth import  logout
from .mixins import CustomLoginRequiredMixin , AdminRequiredMixin


class WelcomePage(PageView):
    template_name = 'pages/welcome.html'


class LoginPage(PageView):
    template_name = 'pages/login.html'

class RegisterPage(PageView):
    template_name = 'pages/register.html'


class ComingSoonPage(PageView):
    template_name = 'pages/comming_soon.html'


# @login_required
class DashboardPage(PageView):
    template_name = 'pages/user/user_dashboard.html'

class AppointmentsPage(PageView):
    template_name = 'management/management_appointments.html'


def logout_view(request):
    logout(request)
    redirect('page:welcome') 

