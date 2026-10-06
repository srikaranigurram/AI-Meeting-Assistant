import React, { useState } from 'react';
import { DemoNavBar } from './components/common/DemoNavBar';
import { BrandHero } from './components/common/BrandHero';
import { LoginForm } from './components/auth/LoginForm';
import { RegisterForm } from './components/auth/RegisterForm';
import { ForgotPasswordForm } from './components/auth/ForgotPasswordForm';
import { DashboardView } from './components/dashboard/DashboardView';
import { ToastContainer } from './components/common/Toast';
import { AuthProvider } from './context/AuthContext';
import './styles/global.css';
import './styles/auth.css';
import './styles/toast.css';
import './styles/demoNav.css';
import './styles/dashboard.css';

const AuthAppContent = () => {
  const [currentView, setCurrentView] = useState(() => {
    return localStorage.getItem('ai_meeting_auth_token') ? 'dashboard' : 'login';
  });

  return (
    <div className="auth-app-root">
      {/* Top Demo Navigation Bar */}
      <DemoNavBar
        currentView={currentView}
        onViewChange={(view) => setCurrentView(view)}
      />

      <ToastContainer />

      {currentView === 'dashboard' ? (
        /* Full Modern AI Dashboard View */
        <DashboardView
          onNavigateLogin={() => setCurrentView('login')}
          onNavigateRegister={() => setCurrentView('register')}
        />
      ) : (
        /* Split Hero / Form Layout for Auth Screens */
        <div className="auth-page-container">
          <main className="auth-wrapper">
            {/* Left Column: Branding Hero */}
            <BrandHero />

            {/* Right Column: Dynamic Form Screen */}
            {currentView === 'login' && (
              <LoginForm
                onNavigateRegister={() => setCurrentView('register')}
                onNavigateForgotPassword={() => setCurrentView('forgot-password')}
                onSuccess={() => setCurrentView('dashboard')}
              />
            )}

            {currentView === 'register' && (
              <RegisterForm
                onNavigateLogin={() => setCurrentView('login')}
                onSuccess={() => setCurrentView('dashboard')}
              />
            )}

            {currentView === 'forgot-password' && (
              <ForgotPasswordForm
                onNavigateLogin={() => setCurrentView('login')}
              />
            )}
          </main>
        </div>
      )}
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <AuthAppContent />
    </AuthProvider>
  );
}
