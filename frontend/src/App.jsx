import React, { useState, useMemo, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { createAppTheme } from './theme';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import RoleDashboard from './components/RoleDashboard';
import Login from './components/Login';
import CasesList from './components/CasesList';
import DocumentsList from './components/DocumentsList';
import UsersList from './components/UsersList';
import Settings from './components/Settings';
import Audit from './pages/Audit';
import { CircularProgress, Box } from '@mui/material';
import { useTranslation } from 'react-i18next';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" />;
};

function AppContent() {
  const { i18n } = useTranslation();
  const [mode, setMode] = useState(() => {
    const savedMode = localStorage.getItem('themeMode');
    return savedMode || 'light';
  });

  const direction = i18n.language === 'ar' ? 'rtl' : 'ltr';
  const theme = useMemo(() => createAppTheme(mode, direction), [mode, direction]);

  useEffect(() => {
    document.documentElement.dir = direction;
    document.documentElement.lang = i18n.language;
  }, [direction, i18n.language]);

  const toggleTheme = () => {
    setMode((prevMode) => {
      const newMode = prevMode === 'light' ? 'dark' : 'light';
      localStorage.setItem('themeMode', newMode);
      return newMode;
    });
  };

  const { isAuthenticated } = useAuth();

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated ? <Navigate to="/" /> : <Login />
          }
        />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout onToggleTheme={toggleTheme} mode={mode}>
                <RoleDashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/casos"
          element={
            <ProtectedRoute>
              <Layout onToggleTheme={toggleTheme} mode={mode}>
                <CasesList />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/documentos"
          element={
            <ProtectedRoute>
              <Layout onToggleTheme={toggleTheme} mode={mode}>
                <DocumentsList />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/usuarios"
          element={
            <ProtectedRoute>
              <Layout onToggleTheme={toggleTheme} mode={mode}>
                <UsersList />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/configuracion"
          element={
            <ProtectedRoute>
              <Layout onToggleTheme={toggleTheme} mode={mode}>
                <Settings />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/auditoria"
          element={
            <ProtectedRoute>
              <Layout onToggleTheme={toggleTheme} mode={mode}>
                <Audit />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </ThemeProvider>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;
