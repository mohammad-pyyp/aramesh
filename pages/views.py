from django.contrib.auth.decorators import login_required 
from django.shortcuts import  redirect
from django.views.generic import TemplateView as PageView
from django.contrib.auth import  logout
from .mixins import CustomLoginRequiredMixin , AdminRequiredMixin

# ------------------ Public ------------------
class HomePage(PageView):
    template_name = 'pages/public/home.html'


class CommingSoonPage(PageView):
    template_name = 'comming_soon.html'


def logout_view(request):
    logout(request)
    return redirect('pages:home') 


class LoginPage(PageView):
    template_name = 'pages/public/user/auth/login.html'


class RegisterPage(PageView):
    template_name = 'pages/public/user/auth/register.html'

# ------------------ User ------------------

class DashboardPage(PageView):
    template_name = 'pages/user/dashboard.html'


# ------------------ Admin ------------------

class AppointmentsPage(PageView):
    template_name = 'pages/admin/appointments.html'


