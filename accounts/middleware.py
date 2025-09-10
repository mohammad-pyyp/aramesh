# accounts/middleware.py
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Custom JWT middleware for handling token authentication
    and automatic token refresh
    """
    
    def process_request(self, request):
        # Skip middleware for certain paths
        skip_paths = ['/admin/', '/api-auth/', '/static/', '/media/']
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Check for Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                # Validate token
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                
                # Get user
                try:
                    user = User.objects.get(id=user_id, is_active=True)
                    request.user = user
                    request._jwt_token = access_token
                except User.DoesNotExist:
                    request.user = None
                    
            except (TokenError, InvalidToken) as e:
                logger.debug(f"Invalid JWT token: {e}")
                request.user = None
        
        return None


class JWTResponseMiddleware(MiddlewareMixin):
    """
    Middleware to handle JWT token refresh in responses
    """
    
    def process_response(self, request, response):
        # Only process JSON responses
        if not isinstance(response, JsonResponse):
            return response
        
        # Check if user is authenticated and has a JWT token
        if hasattr(request, '_jwt_token') and request._jwt_token:
            # Add token info to response headers (optional)
            response['X-Token-Type'] = 'Bearer'
            response['X-Token-Expires'] = request._jwt_token['exp']
        
        return response
