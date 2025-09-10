from django.shortcuts import render

# Create your views here.

def welcome_page(request):
    """Render the welcome page"""
    return render(request, 'welcome_page.html')

def coming_soon(request):
    """Render the coming soon page"""
    return render(request, 'comming_soon.html')

def user_dashboard(request):
    """Render the user dashboard page"""
    return render(request, 'user_dashboard.html')