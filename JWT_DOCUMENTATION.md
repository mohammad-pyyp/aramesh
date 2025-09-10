# JWT Authentication System Documentation

## Overview
This project implements a comprehensive JWT (JSON Web Token) authentication system using Django REST Framework SimpleJWT. The system provides secure authentication with phone number-based OTP verification.

## Features

### Backend Features
- **OTP-based Authentication**: Phone number verification with SMS OTP
- **JWT Token Management**: Access and refresh token system
- **Token Blacklisting**: Secure logout with token invalidation
- **Custom Claims**: Additional user data in JWT payload
- **Token Refresh**: Automatic token renewal
- **Multi-device Logout**: Logout from all devices
- **Token Verification**: Validate token without authentication

### Frontend Features
- **JWT Client**: Comprehensive JavaScript client for token management
- **Automatic Refresh**: Background token renewal
- **Local Storage**: Secure token persistence
- **Error Handling**: Graceful handling of authentication errors
- **API Integration**: Seamless integration with Django REST API

## Installation

### Backend Dependencies
```bash
pip install djangorestframework-simplejwt
pip install django-cors-headers
```

### Frontend Dependencies
Include the JWT client in your HTML:
```html
<script src="/static/js/jwt-client.js"></script>
```

## Configuration

### Django Settings
The JWT system is configured in `config/settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # 1 hour
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # 7 days
    'ROTATE_REFRESH_TOKENS': True,                   # Rotate refresh tokens
    'BLACKLIST_AFTER_ROTATION': True,                # Blacklist old tokens
    'UPDATE_LAST_LOGIN': True,                       # Update last login time
    # ... other settings
}
```

## API Endpoints

### Authentication Endpoints
- `POST /api/send-otp/` - Send OTP to phone number
- `POST /api/register/` - Register user with OTP
- `POST /api/login/` - Login user with OTP

### Token Management Endpoints
- `POST /api/token/refresh/` - Refresh access token
- `POST /api/token/verify/` - Verify token validity
- `POST /api/logout/` - Logout (blacklist refresh token)
- `POST /api/logout-all/` - Logout from all devices

### User Endpoints
- `GET /api/dashboard/` - Get user profile
- `PATCH /api/profile/` - Update user profile

## Usage Examples

### Frontend JavaScript Usage

#### Initialize JWT Client
```javascript
// JWT client is automatically initialized as window.jwtClient
const jwtClient = window.jwtClient;
```

#### Send OTP
```javascript
try {
    const response = await jwtClient.sendOTP('09123456789', 'register');
    console.log('OTP sent:', response.message);
} catch (error) {
    console.error('OTP send failed:', error.message);
}
```

#### Register User
```javascript
try {
    const response = await jwtClient.register('09123456789', '123456', 'John', 'Doe');
    console.log('Registration successful:', response.data.user);
    // Tokens are automatically saved
} catch (error) {
    console.error('Registration failed:', error.message);
}
```

#### Login User
```javascript
try {
    const response = await jwtClient.login('09123456789', '123456');
    console.log('Login successful:', response.data.user);
    // Tokens are automatically saved
} catch (error) {
    console.error('Login failed:', error.message);
}
```

#### Make Authenticated Requests
```javascript
try {
    const response = await jwtClient.apiRequest('/dashboard/');
    const data = await response.json();
    console.log('User profile:', data);
} catch (error) {
    console.error('API request failed:', error);
}
```

#### Logout
```javascript
try {
    await jwtClient.logout();
    console.log('Logged out successfully');
} catch (error) {
    console.error('Logout failed:', error);
}
```

#### Check Authentication Status
```javascript
if (jwtClient.isAuthenticated()) {
    console.log('User is authenticated');
    const userData = jwtClient.getUserData();
    console.log('User data:', userData);
} else {
    console.log('User is not authenticated');
}
```

### Backend Python Usage

#### Create Tokens for User
```python
from accounts.jwt_utils import create_tokens_for_user

tokens = create_tokens_for_user(user)
print(f"Access token: {tokens['access']}")
print(f"Refresh token: {tokens['refresh']}")
```

#### Verify Token
```python
from accounts.jwt_utils import JWTManager

result = JWTManager.verify_token(token_string)
if result['valid']:
    user = result['user']
    print(f"Token is valid for user: {user.phone}")
else:
    print(f"Token is invalid: {result['error']}")
```

#### Refresh Token
```python
from accounts.jwt_utils import refresh_access_token

try:
    new_tokens = refresh_access_token(refresh_token_string)
    print(f"New access token: {new_tokens['access']}")
except Exception as e:
    print(f"Token refresh failed: {e}")
```

## Security Features

### Token Security
- **Short-lived Access Tokens**: 1 hour expiration
- **Long-lived Refresh Tokens**: 7 days expiration
- **Token Rotation**: New refresh token on each refresh
- **Blacklisting**: Invalidated tokens are blacklisted
- **Custom Claims**: Additional security information in tokens

### Authentication Security
- **OTP Verification**: Phone number verification required
- **Rate Limiting**: OTP request limits
- **Token Validation**: Server-side token verification
- **Secure Storage**: Tokens stored securely in localStorage

## Error Handling

### Common Error Responses
```json
{
    "success": false,
    "message": "خطا در احراز هویت",
    "data": {}
}
```

### Token Errors
- **401 Unauthorized**: Invalid or expired token
- **400 Bad Request**: Invalid token format
- **403 Forbidden**: Token blacklisted

### OTP Errors
- **429 Too Many Requests**: Rate limit exceeded
- **400 Bad Request**: Invalid OTP or phone number

## Middleware

### JWT Authentication Middleware
The `JWTAuthenticationMiddleware` automatically:
- Extracts JWT tokens from Authorization headers
- Validates tokens
- Sets user context for requests
- Handles token expiration

### JWT Response Middleware
The `JWTResponseMiddleware` adds:
- Token information to response headers
- Token expiration timestamps
- Authentication status indicators

## Customization

### Custom Token Claims
Add custom claims to JWT tokens by modifying the `CustomTokenObtainPairSerializer`:

```python
@classmethod
def get_token(cls, user):
    token = super().get_token(user)
    
    # Add custom claims
    token['phone'] = user.phone
    token['first_name'] = user.first_name
    token['last_name'] = user.last_name
    token['is_staff'] = user.is_staff
    
    return token
```

### Token Lifetime Configuration
Modify token lifetimes in settings:

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),  # 30 minutes
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),     # 14 days
    # ... other settings
}
```

## Troubleshooting

### Common Issues

#### Token Expiration
- **Problem**: 401 Unauthorized errors
- **Solution**: Implement automatic token refresh

#### CORS Issues
- **Problem**: Cross-origin requests blocked
- **Solution**: Configure CORS settings in Django

#### Token Storage
- **Problem**: Tokens lost on page refresh
- **Solution**: Ensure localStorage is available and working

### Debug Mode
Enable debug logging for JWT operations:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'accounts.jwt_utils': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Best Practices

### Security
1. Always use HTTPS in production
2. Implement proper token rotation
3. Use secure token storage
4. Validate tokens on every request
5. Implement proper logout functionality

### Performance
1. Use token refresh to avoid re-authentication
2. Cache user data appropriately
3. Implement proper error handling
4. Use middleware for automatic token handling

### User Experience
1. Provide clear error messages
2. Implement automatic token refresh
3. Handle network errors gracefully
4. Provide loading states for authentication

## Migration Guide

### From Session Authentication
1. Install `djangorestframework-simplejwt`
2. Update `REST_FRAMEWORK` settings
3. Replace session authentication with JWT
4. Update frontend to use JWT client
5. Test authentication flow

### From Token Authentication
1. Install `djangorestframework-simplejwt`
2. Update authentication classes
3. Implement token refresh logic
4. Update frontend token handling
5. Test token management

## Support

For issues and questions:
1. Check the Django REST Framework SimpleJWT documentation
2. Review the JWT client implementation
3. Check server logs for authentication errors
4. Verify token configuration and settings
