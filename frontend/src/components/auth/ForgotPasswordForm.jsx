import React, { useState } from 'react';
import { FormInput } from '../common/FormInput';
import { validateEmail } from '../../utils/validation';
import { useAuth } from '../../context/AuthContext';

export const ForgotPasswordForm = ({ onNavigateLogin }) => {
  const { forgotPassword, showToast } = useAuth();

  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [touched, setTouched] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleChange = (e) => {
    setEmail(e.target.value);
    if (error) setError('');
  };

  const handleBlur = () => {
    setTouched(true);
    const { isValid, message } = validateEmail(email);
    if (!isValid) setError(message);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setTouched(true);

    const emailValidation = validateEmail(email);
    if (!emailValidation.isValid) {
      setError(emailValidation.message);
      return;
    }

    setIsSubmitting(true);
    try {
      await forgotPassword(email.trim());
      setIsSubmitted(true);
    } catch (err) {
      showToast('error', 'Reset Request Failed', err.message || 'Unable to process reset request.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickFill = () => {
    setEmail('alex.smith@company.com');
    setTouched(true);
    setError('');
    showToast('info', 'Demo Filled', 'Sample recovery email populated.');
  };

  return (
    <div className="auth-form-panel">
      <div className="auth-form-header">
        <h2>Reset your password</h2>
        <p>Enter your verified email and we'll send you recovery instructions</p>
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
            id="btn-reset-quickfill"
            title="Auto-populate sample email"
          >
            ⚡ Auto-Fill
          </button>
        </div>
      </div>

      {isSubmitted ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', textAlign: 'center', padding: '1rem 0' }}>
          <div style={{ fontSize: '3rem' }}>✉️</div>
          <h3 style={{ fontSize: '1.3rem' }}>Check your email</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.6' }}>
            We have dispatched password reset instructions to <strong style={{ color: 'var(--text-primary)' }}>{email}</strong>.
          </p>
          <button
            type="button"
            onClick={onNavigateLogin}
            className="btn-primary"
            style={{ marginTop: '1rem' }}
          >
            Return to Sign In
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="auth-form" noValidate>
          <FormInput
            id="reset-email"
            name="email"
            label="Email Address"
            type="email"
            value={email}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="alex.smith@company.com"
            error={touched ? error : ''}
            isValid={touched && !error && email.length > 0}
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

          <button
            type="submit"
            className="btn-primary"
            disabled={isSubmitting}
            id="btn-reset-submit"
          >
            {isSubmitting ? (
              <>
                <div className="spinner" />
                <span>Sending instructions...</span>
              </>
            ) : (
              <>
                <span>Send Recovery Link</span>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M5 12h14"/>
                  <path d="m12 5 7 7-7 7"/>
                </svg>
              </>
            )}
          </button>

          <div className="auth-footer-prompt">
            <span>Remembered your credentials? </span>
            <button
              type="button"
              onClick={onNavigateLogin}
              className="auth-toggle-btn"
            >
              Sign in
            </button>
          </div>
        </form>
      )}
    </div>
  );
};
