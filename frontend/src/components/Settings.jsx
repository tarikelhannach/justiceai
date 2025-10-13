import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Divider,
  Switch,
  FormControlLabel,
  Grid,
} from '@mui/material';
import {
  Save as SaveIcon,
  Person as PersonIcon,
  Lock as LockIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const Settings = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);
  
  // Profile settings
  const [profileData, setProfileData] = useState({
    name: user?.name || '',
    email: user?.email || '',
  });
  
  // Password change
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  
  // Notification settings
  const [notifications, setNotifications] = useState({
    emailNotifications: true,
    caseUpdates: true,
    documentUploads: true,
    deadlineReminders: true,
  });

  const handleUpdateProfile = async () => {
    try {
      await api.put('/users/me', profileData);
      setSuccess(t('settings.profileUpdated', 'Perfil actualizado correctamente'));
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || t('common.error'));
      setSuccess(null);
    }
  };

  const handleChangePassword = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setError(t('settings.passwordMismatch', 'Las contraseñas no coinciden'));
      return;
    }
    
    try {
      await api.post('/auth/change-password', {
        current_password: passwordData.currentPassword,
        new_password: passwordData.newPassword,
      });
      setSuccess(t('settings.passwordChanged', 'Contraseña actualizada correctamente'));
      setError(null);
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    } catch (err) {
      setError(err.response?.data?.detail || t('common.error'));
      setSuccess(null);
    }
  };

  const handleSaveNotifications = () => {
    localStorage.setItem('notificationSettings', JSON.stringify(notifications));
    setSuccess(t('settings.notificationsSaved', 'Preferencias guardadas'));
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight={700} mb={3}>
        {t('navigation.settings')}
      </Typography>

      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 3 }}>
          {success}
        </Alert>
      )}

      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Profile Settings */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" alignItems="center" mb={2}>
              <PersonIcon sx={{ mr: 1 }} />
              <Typography variant="h6" fontWeight={600}>
                {t('settings.profile', 'Perfil')}
              </Typography>
            </Box>
            <Divider sx={{ mb: 2 }} />
            
            <Box display="flex" flexDirection="column" gap={2}>
              <TextField
                label={t('users.name', 'Nombre')}
                value={profileData.name}
                onChange={(e) => setProfileData({ ...profileData, name: e.target.value })}
                fullWidth
              />
              <TextField
                label={t('users.email', 'Correo')}
                type="email"
                value={profileData.email}
                onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                fullWidth
              />
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleUpdateProfile}
              >
                {t('common.save')}
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Password Change */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" alignItems="center" mb={2}>
              <LockIcon sx={{ mr: 1 }} />
              <Typography variant="h6" fontWeight={600}>
                {t('settings.changePassword', 'Cambiar Contraseña')}
              </Typography>
            </Box>
            <Divider sx={{ mb: 2 }} />
            
            <Box display="flex" flexDirection="column" gap={2}>
              <TextField
                label={t('settings.currentPassword', 'Contraseña Actual')}
                type="password"
                value={passwordData.currentPassword}
                onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
                fullWidth
              />
              <TextField
                label={t('settings.newPassword', 'Nueva Contraseña')}
                type="password"
                value={passwordData.newPassword}
                onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                fullWidth
              />
              <TextField
                label={t('settings.confirmPassword', 'Confirmar Contraseña')}
                type="password"
                value={passwordData.confirmPassword}
                onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                fullWidth
              />
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleChangePassword}
              >
                {t('settings.changePassword', 'Cambiar Contraseña')}
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Notification Preferences */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" alignItems="center" mb={2}>
              <NotificationsIcon sx={{ mr: 1 }} />
              <Typography variant="h6" fontWeight={600}>
                {t('settings.notifications', 'Notificaciones')}
              </Typography>
            </Box>
            <Divider sx={{ mb: 2 }} />
            
            <Box display="flex" flexDirection="column" gap={1}>
              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.emailNotifications}
                    onChange={(e) => setNotifications({ ...notifications, emailNotifications: e.target.checked })}
                  />
                }
                label={t('settings.emailNotifications', 'Notificaciones por correo')}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.caseUpdates}
                    onChange={(e) => setNotifications({ ...notifications, caseUpdates: e.target.checked })}
                  />
                }
                label={t('settings.caseUpdates', 'Actualizaciones de casos')}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.documentUploads}
                    onChange={(e) => setNotifications({ ...notifications, documentUploads: e.target.checked })}
                  />
                }
                label={t('settings.documentUploads', 'Nuevos documentos')}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.deadlineReminders}
                    onChange={(e) => setNotifications({ ...notifications, deadlineReminders: e.target.checked })}
                  />
                }
                label={t('settings.deadlineReminders', 'Recordatorios de plazos')}
              />
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSaveNotifications}
                sx={{ mt: 2, alignSelf: 'flex-start' }}
              >
                {t('common.save')}
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Settings;
