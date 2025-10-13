import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Box, CircularProgress, Typography, Alert, Button } from '@mui/material';
import { Lock as LockIcon } from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';

const PrivateRoute = ({ 
  children, 
  requiredRole = null,
  requiredRoles = [],
  redirectTo = '/login',
  fallbackPath = '/'
}) => {
  const { isAuthenticated, loading, user } = useAuth();
  const location = useLocation();
  const { t } = useTranslation();

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          gap: 2,
        }}
      >
        <CircularProgress size={60} />
        <Typography variant="body2" color="text.secondary">
          {t('common.loading') || 'Cargando...'}
        </Typography>
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  const allowedRoles = requiredRole ? [requiredRole] : requiredRoles;
  
  if (allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          p: 4,
          gap: 3,
        }}
      >
        <LockIcon sx={{ fontSize: 80, color: 'error.main' }} />
        <Typography variant="h4" fontWeight={600} color="error">
          {t('errors.accessDenied') || 'Acceso Denegado'}
        </Typography>
        <Alert severity="error" sx={{ maxWidth: 500 }}>
          <Typography variant="body1">
            {t('errors.insufficientPermissions') || 
             'No tienes los permisos necesarios para acceder a esta página.'}
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            {t('errors.requiredRole') || 'Rol requerido'}: <strong>{allowedRoles.join(', ')}</strong>
          </Typography>
          <Typography variant="body2">
            {t('errors.yourRole') || 'Tu rol'}: <strong>{user?.role || 'desconocido'}</strong>
          </Typography>
        </Alert>
        <Button
          variant="contained"
          onClick={() => window.location.href = fallbackPath}
          sx={{ mt: 2 }}
        >
          {t('common.goBack') || 'Volver al inicio'}
        </Button>
      </Box>
    );
  }

  return children;
};

export default PrivateRoute;
