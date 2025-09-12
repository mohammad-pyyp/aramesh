from django.contrib.auth.decorators import login_required 
from django.shortcuts import  redirect
from django.views.generic import TemplateView as PageView
from django.contrib.auth import  logout



class WelcomePage(PageView):
    template_name = 'pages/user/welcome_page.html'

class LoginPage(PageView):
    template_name = 'pages/user/login.html'

class RegisterPage(PageView):
    template_name = 'pages/user/register.html'


class ComingSoonPage(PageView):
    template_name = 'pages/user/comming_soon.html'


# @login_required
class DashboardPage(PageView):
    template_name = 'pages/user/user_dashboard.html'

class AppointmentsPage(PageView):
    template_name = 'management/management_appointments.html'


def logout_view(request):
    logout(request)
    redirect('page:welcome') 

