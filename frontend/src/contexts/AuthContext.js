// frontend/src/contexts/AuthContext.js - Contexto de Autenticación

import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('access_token'));

  // Configurar axios
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, [token]);

  // Verificar autenticación al cargar
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const response = await axios.get('/api/v1/auth/me');
          setUser(response.data);
        } catch (error) {
          console.error('Auth check failed:', error);
          localStorage.removeItem('access_token');
          setToken(null);
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  const login = async (email, password, twoFactorCode = null) => {
    try {
      setLoading(true);
      
      const loginData = {
        username: email,
        password: password,
      };

      if (twoFactorCode) {
        loginData.two_factor_code = twoFactorCode;
      }

      const response = await axios.post('/api/v1/auth/token', loginData);
      
      const { access_token, refresh_token, user: userData } = response.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      setToken(access_token);
      setUser(userData);
      
      toast.success('Inicio de sesión exitoso');
      return { success: true };
      
    } catch (error) {
      const message = error.response?.data?.detail || 'Error al iniciar sesión';
      toast.error(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await axios.post('/api/v1/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setToken(null);
      setUser(null);
      toast.success('Sesión cerrada');
    }
  };

  const refreshToken = async () => {
    try {
      const refreshTokenValue = localStorage.getItem('refresh_token');
      if (!refreshTokenValue) {
        throw new Error('No refresh token');
      }

      const response = await axios.post('/api/v1/auth/refresh', {
        refresh_token: refreshTokenValue,
      });

      const { access_token } = response.data;
      localStorage.setItem('access_token', access_token);
      setToken(access_token);
      
      return access_token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      logout();
      throw error;
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await axios.put('/api/v1/auth/profile', profileData);
      setUser(response.data);
      toast.success('Perfil actualizado');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Error al actualizar perfil';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const changePassword = async (currentPassword, newPassword) => {
    try {
      await axios.put('/api/v1/auth/password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      toast.success('Contraseña actualizada');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Error al cambiar contraseña';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const value = {
    user,
    loading,
    login,
    logout,
    refreshToken,
    updateProfile,
    changePassword,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
