from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
# your views.py
from django.views import View
from .forms import UserRegistrationForm
# Assuming you have a login URL name, e.g., 'accounts:login'
from django.urls import reverse_lazy 

from django.views.generic import TemplateView as PageView
from django.contrib.auth import  logout , login
from .mixins import CustomLoginRequiredMixin , AdminRequiredMixin

# ------------------ Public ------------------

class RegistrationView(CreateView):
    form_class = UserRegistrationForm
    success_url = reverse_lazy('pages:home')
    template_name = 'pages/public/user/auth/register.html'
    
    def form_valid(self, form):
        user = form.save()
        return super().form_valid(form)


class RegistrationView(View):
    form_class = UserRegistrationForm
    template_name = 'pages/public/user/auth/register.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(self.request, user)

            return redirect(reverse_lazy('pages:home'))
        return render(request, self.template_name, {'form': form})



class HomePage(PageView):
    template_name = 'pages/public/home.html'


class CommingSoonPage(PageView):
    template_name = 'comming_soon.html'


def logout_view(request):
    logout(request)
    return redirect('pages:home') 


class LoginPage(PageView):
    template_name = 'pages/public/user/auth/login.html'


# ------------------ User ------------------

class DashboardPage(PageView):
    template_name = 'pages/user/dashboard.html'


# ------------------ Admin ------------------

class AppointmentsPage(PageView):
    template_name = 'pages/admin/appointments.html'


