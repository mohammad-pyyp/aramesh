from django.contrib.auth.decorators import login_required 
from django.shortcuts import  redirect
from django.views.generic import TemplateView as PageView
from django.contrib.auth import  logout
from .mixins import CustomLoginRequiredMixin , AdminRequiredMixin


class CommingSoon(PageView):
    template_name = 'comming_soon.html'

class HomePage(PageView):
    template_name = 'pages/public/home.html'


class LoginPage(PageView):
    template_name = 'pages/user/login.html'

class RegisterPage(PageView):
    template_name = 'pages/user/register.html'


class ComingSoonPage(PageView):
    template_name = 'pages/comming_soon.html'


# @login_required
class DashboardPage(PageView):
    template_name = 'pages/user/dashboard.html'


class AppointmentsPage(PageView):
    template_name = 'pages/admin/appointments.html'


def logout_view(request):
    logout(request)
    return redirect('pages:home') 

