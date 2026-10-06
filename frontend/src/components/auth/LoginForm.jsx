import React, { useState, useEffect } from 'react';
import { FormInput } from '../common/FormInput';
import { PasswordInput } from '../common/PasswordInput';
import { validateEmail } from '../../utils/validation';
import { authApi } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

export const LoginForm = ({ onNavigateRegister, onNavigateForgotPassword, onSuccess }) => {
  const { login, showToast } = useAuth();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false,
  });

  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Load remembered email if present
  useEffect(() => {
    const savedEmail = authApi.getRememberedEmail();
    if (savedEmail) {
      setFormData((prev) => ({
        ...prev,
        email: savedEmail,
        rememberMe: true,
      }));
    }
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const val = type === 'checkbox' ? checked : value;

    setFormData((prev) => ({
      ...prev,
      [name]: val,
    }));

    // Clear error on change if field was touched
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));

    if (name === 'email') {
      const { isValid, message } = validateEmail(value);
      if (!isValid) {
        setErrors((prev) => ({ ...prev, email: message }));
      }
    } else if (name === 'password') {
      if (!value.trim()) {
        setErrors((prev) => ({ ...prev, password: 'Password is required.' }));
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate all fields
    const emailValidation = validateEmail(formData.email);
    const newErrors = {};

    if (!emailValidation.isValid) {
      newErrors.email = emailValidation.message;
    }

    if (!formData.password) {
      newErrors.password = 'Password is required.';
    }

    setErrors(newErrors);
    setTouched({ email: true, password: true });

    if (Object.keys(newErrors).length > 0) {
      return;
    }

    setIsSubmitting(true);
    try {
      await login({
        email: formData.email.trim(),
        password: formData.password,
        rememberMe: formData.rememberMe,
      });

      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      showToast('error', 'Login Failed', err.message || 'Unable to sign in. Please verify your credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSocialClick = (provider) => {
    showToast('info', 'SSO Integration', `${provider} Single Sign-On will be activated with backend OAuth.`);
  };

  const handleQuickFill = () => {
    setFormData({
      email: 'alex.smith@company.com',
      password: 'Password123!',
      rememberMe: true,
    });
    setTouched({ email: true, password: true });
    setErrors({});
    showToast('info', 'Demo Filled', 'Sample login credentials inserted.');
  };

  return (
    <div className="auth-form-panel">
      <div className="auth-form-header">
        <h2>Welcome back</h2>
        <p>Sign in to your AI Meeting Assistant workspace</p>
      </div>

      {/* Demo Helper Banner */}
      <div className="demo-helper-bar">
        <div className="demo-helper-text">
          <span>✨</span>
          <span>Demo Mode</span>
        </div>
        <div className="demo-helper-buttons">
          <button
            type="button"
            className="demo-chip-btn"
            onClick={handleQuickFill}
            id="btn-login-quickfill"
            title="Auto-populate sample login credentials"
          >
            ⚡ Auto-Fill
          </button>
          <button
            type="button"
            className="demo-chip-btn"
            onClick={onSuccess}
            id="btn-login-skip-dashboard"
            title="Jump directly to Dashboard"
          >
            🚀 View Dashboard
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="auth-form" noValidate>
        {/* Email Field */}
        <FormInput
          id="login-email"
          name="email"
          label="Email Address"
          type="email"
          value={formData.email}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="alex.smith@company.com"
          error={touched.email ? errors.email : ''}
          isValid={touched.email && !errors.email && formData.email.length > 0}
          required
          autoComplete="email"
          disabled={isSubmitting}
          icon={
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect width="20" height="16" x="2" y="4" rx="2"/>
              <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
            </svg>
          }
        />

        {/* Password Field */}
        <PasswordInput
          id="login-password"
          name="password"
          label="Password"
          value={formData.password}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Enter your password"
          error={touched.password ? errors.password : ''}
          isValid={touched.password && !errors.password && formData.password.length > 0}
          required
          disabled={isSubmitting}
          autoComplete="current-password"
        />

        {/* Remember Me & Forgot Password Row */}
        <div className="form-options-row">
          <label className="remember-label" htmlFor="remember-me">
            <input
              type="checkbox"
              id="remember-me"
              name="rememberMe"
              checked={formData.rememberMe}
              onChange={handleChange}
              className="custom-checkbox"
              disabled={isSubmitting}
            />
            <span>Remember me</span>
          </label>

          <button
            type="button"
            onClick={onNavigateForgotPassword}
            className="forgot-link"
          >
            Forgot password?
          </button>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="btn-primary"
          disabled={isSubmitting}
          id="btn-login-submit"
        >
          {isSubmitting ? (
            <>
              <div className="spinner" />
              <span>Authenticating...</span>
            </>
          ) : (
            <>
              <span>Sign In</span>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14"/>
                <path d="m12 5 7 7-7 7"/>
              </svg>
            </>
          )}
        </button>

        {/* Divider */}
        <div className="auth-divider">
          <span>Or continue with</span>
        </div>

        {/* Social Buttons */}
        <div className="social-buttons-grid">
          <button
            type="button"
            onClick={() => handleSocialClick('Google')}
            className="btn-social"
            title="Sign in with Google"
          >
            <svg className="social-icon" viewBox="0 0 24 24">
              <path fill="#EA4335" d="M12 5c1.6 0 3 .6 4.1 1.7l3.1-3.1C17.3 1.8 14.8 1 12 1 7.5 1 3.7 3.6 1.9 7.3l3.7 2.9C6.5 7.4 9 5 12 5z"/>
              <path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.7-.2-2.3H12v4.6h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.9z"/>
              <path fill="#FBBC05" d="M5.6 14.8c-.2-.7-.4-1.5-.4-2.3s.2-1.6.4-2.3L1.9 7.3C.7 9.7 0 12.3 0 15s.7 5.3 1.9 7.7l3.7-2.9z"/>
              <path fill="#34A853" d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3 0-5.5-2.4-6.4-5.2L1.9 16c1.8 3.7 5.6 7 10.1 7z"/>
            </svg>
            <span>Google</span>
          </button>

          <button
            type="button"
            onClick={() => handleSocialClick('Microsoft')}
            className="btn-social"
            title="Sign in with Microsoft"
          >
            <svg className="social-icon" viewBox="0 0 23 23">
              <path fill="#f35325" d="M1 1h10v10H1z"/>
              <path fill="#81bc06" d="M12 1h10v10H12z"/>
              <path fill="#05a6f0" d="M1 12h10v10H1z"/>
              <path fill="#ffba08" d="M12 12h10v10H12z"/>
            </svg>
            <span>Microsoft</span>
          </button>
        </div>

        {/* Register Prompt */}
        <div className="auth-footer-prompt">
          <span>Don't have an account? </span>
          <button
            type="button"
            onClick={onNavigateRegister}
            className="auth-toggle-btn"
            id="link-to-register"
          >
            Create an account
          </button>
        </div>
      </form>
    </div>
  );
};
