import React, { useState } from 'react';
import { FormInput } from '../common/FormInput';
import { PasswordInput } from '../common/PasswordInput';
import { PasswordStrengthMeter } from './PasswordStrengthMeter';
import { validateEmail, validateFullName, validatePassword, validateConfirmPassword } from '../../utils/validation';
import { useAuth } from '../../context/AuthContext';

export const RegisterForm = ({ onNavigateLogin, onSuccess }) => {
  const { register, showToast } = useAuth();

  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeTerms: false,
  });

  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const passwordStrength = validatePassword(formData.password);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const val = type === 'checkbox' ? checked : value;

    setFormData((prev) => ({
      ...prev,
      [name]: val,
    }));

    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }

    // Live confirm password check
    if (name === 'confirmPassword' && touched.confirmPassword) {
      const matchResult = validateConfirmPassword(formData.password, val);
      if (!matchResult.isValid) {
        setErrors((prev) => ({ ...prev, confirmPassword: matchResult.message }));
      }
    }
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));

    if (name === 'fullName') {
      const { isValid, message } = validateFullName(value);
      if (!isValid) setErrors((prev) => ({ ...prev, fullName: message }));
    } else if (name === 'email') {
      const { isValid, message } = validateEmail(value);
      if (!isValid) setErrors((prev) => ({ ...prev, email: message }));
    } else if (name === 'password') {
      const { isValid, message } = validatePassword(value);
      if (!isValid) setErrors((prev) => ({ ...prev, password: message }));
    } else if (name === 'confirmPassword') {
      const { isValid, message } = validateConfirmPassword(formData.password, value);
      if (!isValid) setErrors((prev) => ({ ...prev, confirmPassword: message }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const nameValidation = validateFullName(formData.fullName);
    const emailValidation = validateEmail(formData.email);
    const passwordValidation = validatePassword(formData.password);
    const confirmValidation = validateConfirmPassword(formData.password, formData.confirmPassword);

    const newErrors = {};
    if (!nameValidation.isValid) newErrors.fullName = nameValidation.message;
    if (!emailValidation.isValid) newErrors.email = emailValidation.message;
    if (!passwordValidation.isValid) newErrors.password = passwordValidation.message;
    if (!confirmValidation.isValid) newErrors.confirmPassword = confirmValidation.message;
    if (!formData.agreeTerms) newErrors.agreeTerms = 'You must agree to the Terms and Privacy Policy.';

    setErrors(newErrors);
    setTouched({
      fullName: true,
      email: true,
      password: true,
      confirmPassword: true,
      agreeTerms: true,
    });

    if (Object.keys(newErrors).length > 0) {
      return;
    }

    setIsSubmitting(true);
    try {
      await register({
        fullName: formData.fullName.trim(),
        email: formData.email.trim(),
        password: formData.password,
      });

      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      showToast('error', 'Registration Failed', err.message || 'Could not complete registration.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickFill = () => {
    const strongSamplePass = 'SecurePass123!';
    setFormData({
      fullName: 'Sarah Connor',
      email: 'sarah.connor@enterprise.ai',
      password: strongSamplePass,
      confirmPassword: strongSamplePass,
      agreeTerms: true,
    });
    setTouched({
      fullName: true,
      email: true,
      password: true,
      confirmPassword: true,
      agreeTerms: true,
    });
    setErrors({});
    showToast('info', 'Demo Filled', 'Sample registration details populated with strong password.');
  };

  return (
    <div className="auth-form-panel">
      <div className="auth-form-header">
        <h2>Create an account</h2>
        <p>Get started with your intelligent AI Meeting Assistant</p>
      </div>

      {/* Demo Helper Banner */}
      <div className="demo-helper-bar">
        <div className="demo-helper-text">
          <span>✨</span>
          <span>Live Connected</span>
        </div>
        <div className="demo-helper-buttons">
          <button
            type="button"
            className="demo-chip-btn"
            onClick={handleQuickFill}
            id="btn-register-quickfill"
            title="Auto-populate sample registration data"
          >
            ⚡ Auto-Fill
          </button>
          <button
            type="button"
            className="demo-chip-btn"
            onClick={onSuccess}
            id="btn-register-skip-dashboard"
            title="Jump directly to Dashboard"
          >
            🚀 View Dashboard
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="auth-form" noValidate>
        {/* Full Name */}
        <FormInput
          id="register-name"
          name="fullName"
          label="Full Name"
          value={formData.fullName}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Sarah Connor"
          error={touched.fullName ? errors.fullName : ''}
          isValid={touched.fullName && !errors.fullName && formData.fullName.length >= 2}
          required
          autoComplete="name"
          disabled={isSubmitting}
          icon={
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          }
        />

        {/* Email */}
        <FormInput
          id="register-email"
          name="email"
          label="Email Address"
          type="email"
          value={formData.email}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="sarah@company.com"
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

        {/* Password with Strength Meter */}
        <PasswordInput
          id="register-password"
          name="password"
          label="Password"
          value={formData.password}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Create a strong password"
          error={touched.password ? errors.password : ''}
          isValid={touched.password && !errors.password && passwordStrength.isValid}
          required
          disabled={isSubmitting}
          autoComplete="new-password"
        >
          {formData.password.length > 0 && (
            <PasswordStrengthMeter validationResult={passwordStrength} />
          )}
        </PasswordInput>

        {/* Confirm Password */}
        <PasswordInput
          id="register-confirm-password"
          name="confirmPassword"
          label="Confirm Password"
          value={formData.confirmPassword}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Re-enter your password"
          error={touched.confirmPassword ? errors.confirmPassword : ''}
          isValid={touched.confirmPassword && !errors.confirmPassword && formData.confirmPassword.length > 0}
          required
          disabled={isSubmitting}
          autoComplete="new-password"
        />

        {/* Terms and Conditions Checkbox */}
        <div className="form-group">
          <label className="remember-label" htmlFor="agree-terms" style={{ alignItems: 'flex-start' }}>
            <input
              type="checkbox"
              id="agree-terms"
              name="agreeTerms"
              checked={formData.agreeTerms}
              onChange={handleChange}
              className="custom-checkbox"
              disabled={isSubmitting}
              style={{ marginTop: '2px' }}
            />
            <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              I agree to the <a href="#terms" onClick={(e) => e.preventDefault()}>Terms of Service</a> and{' '}
              <a href="#privacy" onClick={(e) => e.preventDefault()}>Privacy Policy</a>.
            </span>
          </label>
          {touched.agreeTerms && errors.agreeTerms && (
            <div className="error-message" style={{ marginTop: '0.2rem' }}>
              <span>{errors.agreeTerms}</span>
            </div>
          )}
        </div>

        {/* Register Submit Button */}
        <button
          type="submit"
          className="btn-primary"
          disabled={isSubmitting}
          id="btn-register-submit"
        >
          {isSubmitting ? (
            <>
              <div className="spinner" />
              <span>Creating your account...</span>
            </>
          ) : (
            <>
              <span>Create Account</span>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14"/>
                <path d="m12 5 7 7-7 7"/>
              </svg>
            </>
          )}
        </button>

        {/* Back to Login */}
        <div className="auth-footer-prompt">
          <span>Already have an account? </span>
          <button
            type="button"
            onClick={onNavigateLogin}
            className="auth-toggle-btn"
            id="link-to-login"
          >
            Sign in
          </button>
        </div>
      </form>
    </div>
  );
};
