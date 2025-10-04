// Authentication Service for QuMail Web
// Handles login, logout, and token management

class AuthService {
  constructor() {
    this.baseURL = process.env.NODE_ENV === 'development' 
            ? '' 
            : process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'; 
            
        this.token = localStorage.getItem('qumail_token');
  }

  // Set authentication token
  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('qumail_token', token);
    } else {
      localStorage.removeItem('qumail_token');
    }
  }

  // Clear authentication token
  clearToken() {
    this.token = null;
    localStorage.removeItem('qumail_token');
  }

  // Get current token
  getToken() {
    return this.token || localStorage.getItem('qumail_token');
  }

  // Get auth headers for API requests
  getAuthHeaders() {
    const token = this.getToken();
    return token ? {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    } : {
      'Content-Type': 'application/json'
    };
  }

  // Login user
  async login(email, password) {
    try {
      const fullUrl = `${this.baseURL}/api/auth/login`; 
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: email.toLowerCase(),
          password,
          display_name: email.split('@')[0] // Auto-generate display name
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `Login failed with status: ${response.status}`);
      }
      // Store token
      this.setToken(data.access_token);

      return data;
    } catch (error) {
      // Provide better console feedback for debugging
            console.error('Login request failed. Check server logs (port 8001).', error); 
            // Re-throw for handling in App.js
            throw new Error(error.message || 'Network or Authentication failed. Check server status.');
        }
  }

  // Logout user
  async logout() {
    try {
      const token = this.getToken();
      if (token) {
        const fullUrl = `${this.baseURL}/api/auth/logout`;
        await fetch(fullUrl, {
          method: 'POST',
          headers: this.getAuthHeaders()
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
      // Continue with local logout even if server logout fails
    } finally {
      this.clearToken();
    }
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.getToken();
  }

  // Get user info from token (demo implementation)
  getUserInfo() {
    const token = this.getToken();
    if (token && token.includes('@')) {
      return {
        email: token,
        display_name: token.split('@')[0],
        sae_id: `qumail_${token.replace('@', '_').replace('.', '_')}`
      };
    }
    return null;
  }
}

// Export singleton instance
const authService = new AuthService();
export default authService;
