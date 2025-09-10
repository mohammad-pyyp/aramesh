# config/urls.py :
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Main app URLs (templates)
    path('', include('core.urls')),
    
    # Accounts app URLs (templates)
    path('accounts/', include('accounts.urls')),
    
    # API urls
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
 
]

