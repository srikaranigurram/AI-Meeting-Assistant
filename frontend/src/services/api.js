/**
 * AI Meeting Assistant - Authentication & API Service
 * 
 * --------------------------------------------------------------------------
 * NOTE FOR BACKEND & DEVOPS TEAM:
 * --------------------------------------------------------------------------
 * This module is pre-configured to connect to the FastAPI backend service.
 * When your backend is deployed or running locally, set VITE_API_URL in your
 * .env file or change USE_MOCK_API to false.
 *
 * Expected Backend Endpoints (FastAPI):
 * - POST /api/v1/auth/login        -> Returns { access_token, token_type, user: { id, email, fullName } }
 * - POST /api/v1/auth/register     -> Returns { access_token, token_type, user: { id, email, fullName } }
 * - POST /api/v1/auth/forgot-password -> Returns { message: "Reset email sent" }
 * --------------------------------------------------------------------------
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Toggle mock mode. When true, simulates realistic network latency and mock responses.
export const USE_MOCK_API = true;

/**
 * Helper to simulate network latency for mock mode
 */
const mockDelay = (ms = 700) => new Promise((resolve) => setTimeout(resolve, ms));

export const authApi = {
  /**
   * Log in user with email & password
   * @param {{ email: string, password: string, rememberMe?: boolean }} credentials
   */
  async login({ email, password, rememberMe = false }) {
    if (USE_MOCK_API) {
      await mockDelay(650);

      // Handle simple mock rejection for demo testing
      if (email.toLowerCase().includes('fail') || password === 'wrongpass') {
        const error = new Error('Invalid email or password. Please try again.');
        error.status = 401;
        throw error;
      }

      const mockUser = {
        id: 'usr_ai_99182',
        email,
        fullName: email.split('@')[0].replace(/[^a-zA-Z]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()) || 'Demo User',
        avatar: null,
        role: 'Pro Member',
      };

      const mockResponse = {
        access_token: 'mock_jwt_token_' + Math.random().toString(36).substring(2),
        token_type: 'bearer',
        user: mockUser,
      };

      if (rememberMe) {
        localStorage.setItem('ai_meeting_remembered_email', email);
      } else {
        localStorage.removeItem('ai_meeting_remembered_email');
      }

      localStorage.setItem('ai_meeting_auth_token', mockResponse.access_token);
      localStorage.setItem('ai_meeting_user', JSON.stringify(mockUser));

      return mockResponse;
    }

    // Real FastAPI Endpoint Call
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(errorData.detail || 'Authentication failed.');
      error.status = response.status;
      throw error;
    }

    const data = await response.json();
    if (rememberMe) {
      localStorage.setItem('ai_meeting_remembered_email', email);
    } else {
      localStorage.removeItem('ai_meeting_remembered_email');
    }
    localStorage.setItem('ai_meeting_auth_token', data.access_token);
    localStorage.setItem('ai_meeting_user', JSON.stringify(data.user));

    return data;
  },

  /**
   * Register a new user
   * @param {{ fullName: string, email: string, password: string }} userData 
   */
  async register({ fullName, email, password }) {
    if (USE_MOCK_API) {
      await mockDelay(800);

      // Handle simple mock rejection if email already taken demo
      if (email.toLowerCase() === 'exists@example.com') {
        const error = new Error('An account with this email address already exists.');
        error.status = 409;
        throw error;
      }

      const mockUser = {
        id: 'usr_ai_' + Math.random().toString(36).substring(2, 9),
        email,
        fullName,
        avatar: null,
        role: 'New Member',
      };

      const mockResponse = {
        access_token: 'mock_jwt_token_' + Math.random().toString(36).substring(2),
        token_type: 'bearer',
        user: mockUser,
      };

      localStorage.setItem('ai_meeting_auth_token', mockResponse.access_token);
      localStorage.setItem('ai_meeting_user', JSON.stringify(mockUser));

      return mockResponse;
    }

    // Real FastAPI Endpoint Call
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ full_name: fullName, email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(errorData.detail || 'Registration failed.');
      error.status = response.status;
      throw error;
    }

    const data = await response.json();
    localStorage.setItem('ai_meeting_auth_token', data.access_token);
    localStorage.setItem('ai_meeting_user', JSON.stringify(data.user));
    return data;
  },

  /**
   * Request password reset link
   * @param {{ email: string }} param0 
   */
  async forgotPassword({ email }) {
    if (USE_MOCK_API) {
      await mockDelay(600);
      return {
        success: true,
        message: `Password reset instructions have been dispatched to ${email}.`,
      };
    }

    // Real FastAPI Endpoint Call
    const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to send password reset email.');
    }

    return await response.json();
  },

  /**
   * Log out user
   */
  logout() {
    localStorage.removeItem('ai_meeting_auth_token');
    localStorage.removeItem('ai_meeting_user');
  },

  /**
   * Check if user is currently logged in locally
   */
  getCurrentUser() {
    try {
      const userStr = localStorage.getItem('ai_meeting_user');
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      return null;
    }
  },

  /**
   * Get remembered email
   */
  getRememberedEmail() {
    return localStorage.getItem('ai_meeting_remembered_email') || '';
  },
};
