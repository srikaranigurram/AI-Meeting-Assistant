import React from 'react';
import { useAuth } from '../../context/AuthContext';

export const DemoNavBar = ({ currentView, onViewChange }) => {
  const { user, login, logout, showToast } = useAuth();

  const handleQuickDemoLogin = async () => {
    try {
      await login({
        email: 'alex.chen@enterprise.ai',
        password: 'Password123!',
        rememberMe: true,
      });
      onViewChange('dashboard');
    } catch {
      showToast('info', 'Demo Session', 'Navigating to Dashboard demo.');
      onViewChange('dashboard');
    }
  };

  const handleSignOut = () => {
    logout();
    onViewChange('login');
  };

  return (
    <header className="demo-nav-container">
      <div className="demo-nav-inner">
        {/* Brand & Demo Pill */}
        <div className="demo-brand" onClick={() => onViewChange('dashboard')} role="button" tabIndex={0}>
          <div className="demo-brand-logo">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              <line x1="12" x2="12" y1="19" y2="22"/>
              <line x1="8" x2="16" y1="22" y2="22"/>
            </svg>
          </div>
          <div className="demo-brand-text">
            <span>AI Meeting Assistant</span>
            <span className="demo-mode-badge">
              <span className="demo-mode-dot" />
              Demo Mode
            </span>
          </div>
        </div>

        {/* Navigation Tabs for Demo Presentation */}
        <nav className="demo-nav-tabs" aria-label="Demo Views Navigation">
          <button
            type="button"
            className={`demo-nav-tab ${currentView === 'login' ? 'active' : ''}`}
            onClick={() => onViewChange('login')}
            id="demo-tab-login"
            title="Demonstrate Sign In Page"
          >
            <span className="demo-nav-tab-icon">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <rect width="18" height="11" x="3" y="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
            </span>
            <span>Sign In</span>
          </button>

          <button
            type="button"
            className={`demo-nav-tab ${currentView === 'register' ? 'active' : ''}`}
            onClick={() => onViewChange('register')}
            id="demo-tab-register"
            title="Demonstrate Sign Up / Register Page"
          >
            <span className="demo-nav-tab-icon">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <line x1="19" x2="19" y1="8" y2="14"/>
                <line x1="22" x2="16" y1="11" y2="11"/>
              </svg>
            </span>
            <span>Sign Up</span>
          </button>

          <button
            type="button"
            className={`demo-nav-tab ${currentView === 'dashboard' ? 'active' : ''}`}
            onClick={() => onViewChange('dashboard')}
            id="demo-tab-dashboard"
            title="Demonstrate AI Meeting Dashboard"
          >
            <span className="demo-nav-tab-icon">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <rect width="7" height="9" x="3" y="3" rx="1"/>
                <rect width="7" height="5" x="14" y="3" rx="1"/>
                <rect width="7" height="9" x="14" y="12" rx="1"/>
                <rect width="7" height="5" x="3" y="16" rx="1"/>
              </svg>
            </span>
            <span>Dashboard</span>
          </button>

          <button
            type="button"
            className={`demo-nav-tab ${currentView === 'forgot-password' ? 'active' : ''}`}
            onClick={() => onViewChange('forgot-password')}
            id="demo-tab-forgot-password"
            title="Demonstrate Forgot Password Flow"
          >
            <span className="demo-nav-tab-icon">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="7.5" cy="15.5" r="5.5"/>
                <path d="m21 2-9.6 9.6"/>
                <path d="m15.5 7.5 3 3L22 7l-3-3"/>
              </svg>
            </span>
            <span>Reset Password</span>
          </button>
        </nav>

        {/* Right Actions */}
        <div className="demo-nav-actions">
          {user ? (
            <div className="demo-user-chip">
              <div className="demo-user-avatar">
                {user.fullName ? user.fullName[0].toUpperCase() : 'U'}
              </div>
              <span className="demo-user-name">{user.fullName || user.email}</span>
              <button
                type="button"
                onClick={handleSignOut}
                className="demo-signout-btn"
                title="Sign out & return to Login"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={handleQuickDemoLogin}
              className="demo-quick-btn"
              title="One-click demo login without typing credentials"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
              <span>Instant Demo</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
