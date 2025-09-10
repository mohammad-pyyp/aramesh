# accounts/jwt_utils.py
"""
JWT utility functions for token management
"""
import logging
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class JWTManager:
    """JWT token management utility class"""
    
    @staticmethod
    def create_tokens_for_user(user):
        """Create access and refresh tokens for a user"""
        try:
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            # Add custom claims
            access['phone'] = user.phone
            access['first_name'] = user.first_name
            access['last_name'] = user.last_name
            access['is_staff'] = user.is_staff
            
            return {
                'access': str(access),
                'refresh': str(refresh),
                'access_expires': access['exp'],
                'refresh_expires': refresh['exp'],
            }
        except Exception as e:
            logger.exception(f"Error creating tokens for user {user.id}: {e}")
            raise
    
    @staticmethod
    def refresh_access_token(refresh_token_string):
        """Refresh access token using refresh token"""
        try:
            refresh_token = RefreshToken(refresh_token_string)
            access_token = refresh_token.access_token
            
            return {
                'access': str(access_token),
                'access_expires': access_token['exp'],
            }
        except TokenError as e:
            logger.debug(f"Token refresh failed: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during token refresh: {e}")
            raise
    
    @staticmethod
    def verify_token(token_string):
        """Verify if a token is valid"""
        try:
            token = AccessToken(token_string)
            user_id = token['user_id']
            
            # Check if user exists and is active
            user = User.objects.get(id=user_id, is_active=True)
            
            return {
                'valid': True,
                'user_id': user_id,
                'user': user,
                'expires': token['exp'],
            }
        except (TokenError, InvalidToken, User.DoesNotExist) as e:
            logger.debug(f"Token verification failed: {e}")
            return {'valid': False, 'error': str(e)}
        except Exception as e:
            logger.exception(f"Unexpected error during token verification: {e}")
            return {'valid': False, 'error': 'Unknown error'}
    
    @staticmethod
    def blacklist_token(refresh_token_string):
        """Blacklist a refresh token"""
        try:
            refresh_token = RefreshToken(refresh_token_string)
            refresh_token.blacklist()
            return True
        except TokenError as e:
            logger.debug(f"Token blacklist failed: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error during token blacklist: {e}")
            return False
    
    @staticmethod
    def get_token_payload(token_string):
        """Get payload from a token without verification"""
        try:
            token = AccessToken(token_string)
            return {
                'user_id': token['user_id'],
                'phone': token.get('phone', ''),
                'first_name': token.get('first_name', ''),
                'last_name': token.get('last_name', ''),
                'is_staff': token.get('is_staff', False),
                'expires': token['exp'],
            }
        except Exception as e:
            logger.debug(f"Error getting token payload: {e}")
            return None
    
    @staticmethod
    def is_token_expired(token_string):
        """Check if a token is expired"""
        try:
            token = AccessToken(token_string)
            exp_timestamp = token['exp']
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            return datetime.now() >= exp_datetime
        except Exception:
            return True


def get_user_from_token(token_string):
    """Get user object from token string"""
    verification_result = JWTManager.verify_token(token_string)
    if verification_result['valid']:
        return verification_result['user']
    return None


def create_tokens_for_user(user):
    """Convenience function to create tokens"""
    return JWTManager.create_tokens_for_user(user)


def refresh_access_token(refresh_token_string):
    """Convenience function to refresh token"""
    return JWTManager.refresh_access_token(refresh_token_string)
