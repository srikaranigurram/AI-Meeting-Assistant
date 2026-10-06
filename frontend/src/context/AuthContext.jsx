import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    // Check initial user from localStorage
    const existingUser = authApi.getCurrentUser();
    if (existingUser) {
      setUser(existingUser);
    }
    setIsLoading(false);
  }, []);

  /**
   * Show a floating toast alert
   * @param {'success' | 'error' | 'info'} type 
   * @param {string} title 
   * @param {string} message 
   */
  const showToast = (type, title, message) => {
    const id = Date.now() + Math.random().toString();
    const newToast = { id, type, title, message };
    setToasts((prev) => [...prev, newToast]);

    setTimeout(() => {
      removeToast(id);
    }, 4500);
  };

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const login = async (credentials) => {
    const response = await authApi.login(credentials);
    setUser(response.user);
    showToast('success', 'Welcome Back!', `Signed in as ${response.user.email}`);
    return response;
  };

  const register = async (userData) => {
    const response = await authApi.register(userData);
    setUser(response.user);
    showToast('success', 'Account Created!', `Welcome to AI Meeting Assistant, ${response.user.fullName}!`);
    return response;
  };

  const forgotPassword = async (email) => {
    const response = await authApi.forgotPassword({ email });
    showToast('info', 'Recovery Sent', response.message || 'Check your inbox for the reset link.');
    return response;
  };

  const logout = () => {
    authApi.logout();
    setUser(null);
    showToast('info', 'Signed Out', 'You have been successfully signed out.');
  };

  const value = {
    user,
    isLoading,
    login,
    register,
    forgotPassword,
    logout,
    toasts,
    showToast,
    removeToast,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
