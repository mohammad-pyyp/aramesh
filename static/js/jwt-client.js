// static/js/jwt-client.js
/**
 * JWT Client Utility for handling authentication tokens
 */
class JWTClient {
    constructor(baseURL = 'http://localhost:8000/api') {
        this.baseURL = baseURL;
        this.accessToken = null;
        this.refreshToken = null;
        this.refreshPromise = null;

        // Load tokens from localStorage
        this.loadTokens();

        // Set up automatic token refresh
        this.setupTokenRefresh();
    }

    /**
     * Load tokens from localStorage
     */
    loadTokens() {
        if (typeof localStorage !== 'undefined') {
            this.accessToken = localStorage.getItem('access_token');
            this.refreshToken = localStorage.getItem('refresh_token');
        }
    }

    /**
     * Save tokens to localStorage
     */
    saveTokens(accessToken, refreshToken) {
        this.accessToken = accessToken;
        this.refreshToken = refreshToken;

        if (typeof localStorage !== 'undefined') {
            localStorage.setItem('access_token', accessToken);
            localStorage.setItem('refresh_token', refreshToken);
        }
    }

    /**
     * Clear tokens from localStorage
     */
    clearTokens() {
        this.accessToken = null;
        this.refreshToken = null;

        if (typeof localStorage !== 'undefined') {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
        }
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!(this.accessToken && this.refreshToken);
    }

    /**
     * Get authorization header
     */
    getAuthHeader() {
        return this.accessToken ? `Bearer ${this.accessToken}` : null;
    }

    /**
     * Make authenticated API request
     */
    async apiRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Add authorization header if available
        const authHeader = this.getAuthHeader();
        if (authHeader) {
            headers['Authorization'] = authHeader;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);

            // If token expired, try to refresh
            if (response.status === 401 && this.refreshToken) {
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    // Retry the request with new token
                    headers['Authorization'] = this.getAuthHeader();
                    return await fetch(url, { ...config, headers });
                }
            }

            return response;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    /**
     * Send OTP to phone number
     */
    async sendOTP(phone, mode = 'register') {
        try {
            const response = await this.apiRequest('/send-otp/', {
                method: 'POST',
                body: JSON.stringify({ phone, mode })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'خطا در ارسال کد');
            }

            return data;
        } catch (error) {
            console.error('Send OTP failed:', error);
            throw error;
        }
    }

    /**
     * Register user with OTP
     */
    async register(phone, otp, firstName = '', lastName = '') {
        try {
            const response = await this.apiRequest('/register/', {
                method: 'POST',
                body: JSON.stringify({ phone, otp, first_name: firstName, last_name: lastName })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'خطا در ثبت‌نام');
            }

            // Save tokens and user data
            this.saveTokens(data.data.access, data.data.refresh);
            this.saveUserData(data.data.user);

            return data;
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    }

    /**
     * Login user with OTP
     */
    async login(phone, otp) {
        try {
            const response = await this.apiRequest('/login/', {
                method: 'POST',
                body: JSON.stringify({ phone, otp })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'خطا در ورود');
            }

            // Save tokens and user data
            this.saveTokens(data.data.access, data.data.refresh);
            this.saveUserData(data.data.user);

            return data;
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    }

    /**
     * Refresh access token
     */
    async refreshAccessToken() {
        if (!this.refreshToken) {
            return false;
        }

        // Prevent multiple simultaneous refresh attempts
        if (this.refreshPromise) {
            return await this.refreshPromise;
        }

        this.refreshPromise = this._performTokenRefresh();

        try {
            const result = await this.refreshPromise;
            return result;
        } finally {
            this.refreshPromise = null;
        }
    }

    /**
     * Perform the actual token refresh
     */
    async _performTokenRefresh() {
        try {
            const response = await fetch(`${this.baseURL}/token/refresh/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ refresh: this.refreshToken })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'خطا در تازه‌سازی توکن');
            }

            // Update access token
            this.accessToken = data.data.access;
            if (typeof localStorage !== 'undefined') {
                localStorage.setItem('access_token', this.accessToken);
            }

            return true;
        } catch (error) {
            console.error('Token refresh failed:', error);
            // Clear tokens on refresh failure
            this.clearTokens();
            return false;
        }
    }

    /**
     * Logout user
     */
    async logout() {
        try {
            if (this.refreshToken) {
                await this.apiRequest('/logout/', {
                    method: 'POST',
                    body: JSON.stringify({ refresh: this.refreshToken })
                });
            }
        } catch (error) {
            console.error('Logout API call failed:', error);
        } finally {
            this.clearTokens();
        }
    }

    /**
     * Logout from all devices
     */
    async logoutAll() {
        try {
            await this.apiRequest('/logout-all/', {
                method: 'POST'
            });
        } catch (error) {
            console.error('Logout all failed:', error);
        } finally {
            this.clearTokens();
        }
    }

    /**
     * Get user profile
     */
    async getProfile() {
        try {
            const response = await this.apiRequest('/dashboard/');
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'خطا در دریافت پروفایل');
            }

            return data;
        } catch (error) {
            console.error('Get profile failed:', error);
            throw error;
        }
    }

    /**
     * Update user profile
     */
    async updateProfile(profileData) {
        try {
            const response = await this.apiRequest('/profile/', {
                method: 'PATCH',
                body: JSON.stringify(profileData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'خطا در به‌روزرسانی پروفایل');
            }

            return data;
        } catch (error) {
            console.error('Update profile failed:', error);
            throw error;
        }
    }

    /**
     * Verify token validity
     */
    async verifyToken() {
        if (!this.accessToken) {
            return false;
        }

        try {
            const response = await this.apiRequest('/token/verify/', {
                method: 'POST',
                body: JSON.stringify({ token: this.accessToken })
            });

            const data = await response.json();
            return response.ok && data.success;
        } catch (error) {
            console.error('Token verification failed:', error);
            return false;
        }
    }

    /**
     * Save user data to localStorage
     */
    saveUserData(userData) {
        if (typeof localStorage !== 'undefined') {
            localStorage.setItem('user', JSON.stringify(userData));
        }
    }

    /**
     * Get user data from localStorage
     */
    getUserData() {
        if (typeof localStorage !== 'undefined') {
            const userData = localStorage.getItem('user');
            return userData ? JSON.parse(userData) : null;
        }
        return null;
    }

    /**
     * Setup automatic token refresh
     */
    setupTokenRefresh() {
        // Check token validity every 5 minutes
        setInterval(async () => {
            if (this.isAuthenticated()) {
                const isValid = await this.verifyToken();
                if (!isValid) {
                    console.log('Token expired, attempting refresh...');
                    await this.refreshAccessToken();
                }
            }
        }, 5 * 60 * 1000); // 5 minutes
    }

    /**
     * Decode JWT token (client-side only)
     */
    decodeToken(token) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(atob(base64).split('').map(function (c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));

            return JSON.parse(jsonPayload);
        } catch (error) {
            console.error('Token decode failed:', error);
            return null;
        }
    }

    /**
     * Check if token is expired
     */
    isTokenExpired(token = this.accessToken) {
        if (!token) return true;

        const payload = this.decodeToken(token);
        if (!payload || !payload.exp) return true;

        const currentTime = Math.floor(Date.now() / 1000);
        return payload.exp < currentTime;
    }
}

// Create global instance
window.jwtClient = new JWTClient();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JWTClient;
}
