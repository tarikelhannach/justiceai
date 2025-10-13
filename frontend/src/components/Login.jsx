import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  IconButton,
  Divider,
  Tab,
  Tabs,
  Checkbox,
  FormControlLabel,
  Link as MuiLink,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  Person,
  Gavel,
  Security,
  QrCode2,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSelector from './LanguageSelector';
import { authAPI } from '../services/api';

const Login = () => {
  const { t } = useTranslation();
  const [tabValue, setTabValue] = useState(0);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [searchParams] = useSearchParams();
  
  const [loginForm, setLoginForm] = useState({
    email: '',
    password: '',
    totp_code: '',
    rememberMe: false,
  });
  
  const [registerForm, setRegisterForm] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const [requires2FA, setRequires2FA] = useState(false);
  const [showPasswordReset, setShowPasswordReset] = useState(false);
  const [resetEmail, setResetEmail] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [resetStep, setResetStep] = useState('request');

  const { login, register } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const savedEmail = localStorage.getItem('remembered_email');
    if (savedEmail) {
      setLoginForm(prev => ({ ...prev, email: savedEmail, rememberMe: true }));
    }

    const token = searchParams.get('reset_token');
    if (token) {
      setResetToken(token);
      setShowPasswordReset(true);
      setResetStep('confirm');
    }
  }, [searchParams]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    setError('');
    setSuccess('');
    setRequires2FA(false);
  };

  const handleLoginChange = (e) => {
    const { name, value, checked, type } = e.target;
    setLoginForm({ 
      ...loginForm, 
      [name]: type === 'checkbox' ? checked : value 
    });
    setError('');
    setSuccess('');
  };

  const handleRegisterChange = (e) => {
    setRegisterForm({ ...registerForm, [e.target.name]: e.target.value });
    setError('');
    setSuccess('');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await authAPI.loginWith2FA(
        loginForm.email,
        loginForm.password,
        loginForm.totp_code || null
      );

      if (loginForm.rememberMe) {
        localStorage.setItem('remembered_email', loginForm.email);
      } else {
        localStorage.removeItem('remembered_email');
      }

      localStorage.setItem('token', result.access_token);
      localStorage.setItem('user', JSON.stringify(result.user));
      
      navigate('/');
    } catch (err) {
      if (err.response?.status === 428) {
        setRequires2FA(true);
        setError(t('auth.require2FA') || 'Se requiere código 2FA');
      } else {
        setError(err.response?.data?.detail || t('auth.loginError'));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (registerForm.password !== registerForm.confirmPassword) {
      setError(t('auth.passwordsNotMatch'));
      return;
    }

    if (registerForm.password.length < 6) {
      setError(t('auth.passwordMinLength'));
      return;
    }

    setLoading(true);
    const result = await register(
      registerForm.email,
      registerForm.name,
      registerForm.password
    );
    
    if (result.success) {
      navigate('/');
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const handlePasswordResetRequest = async () => {
    if (!resetEmail) {
      setError(t('auth.emailRequired') || 'Email requerido');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const result = await authAPI.requestPasswordReset(resetEmail);
      setSuccess(result.message);
      if (result.token) {
        setResetToken(result.token);
        setResetStep('confirm');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al solicitar reset');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordResetConfirm = async () => {
    if (!newPassword || newPassword.length < 6) {
      setError(t('auth.passwordMinLength') || 'Contraseña muy corta');
      return;
    }

    setLoading(true);
    setError('');
    try {
      await authAPI.confirmPasswordReset(resetToken, newPassword);
      setSuccess(t('auth.passwordResetSuccess') || 'Contraseña actualizada');
      setTimeout(() => {
        setShowPasswordReset(false);
        setResetStep('request');
        setResetEmail('');
        setResetToken('');
        setNewPassword('');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al resetear contraseña');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        py: 4,
        position: 'relative',
      }}
    >
      <Box sx={{ position: 'absolute', top: 20, right: 20 }}>
        <LanguageSelector />
      </Box>

      <Container maxWidth="sm">
        <Paper
          elevation={24}
          sx={{
            p: 4,
            borderRadius: 3,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
          }}
        >
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
              <Gavel sx={{ fontSize: 48, color: '#667eea', mr: 1 }} />
            </Box>
            <Typography variant="h4" sx={{ fontWeight: 700, color: '#667eea', mb: 1 }}>
              {t('branding.appName')}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {t('branding.country')}
            </Typography>
          </Box>

          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            variant="fullWidth"
            sx={{ mb: 3 }}
          >
            <Tab label={t('auth.login')} />
            <Tab label={t('auth.register')} />
          </Tabs>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
              {success}
            </Alert>
          )}

          {tabValue === 0 ? (
            <form onSubmit={handleLogin}>
              <TextField
                fullWidth
                label={t('auth.email')}
                name="email"
                type="email"
                value={loginForm.email}
                onChange={handleLoginChange}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Email />
                    </InputAdornment>
                  ),
                }}
              />

              <TextField
                fullWidth
                label={t('auth.password')}
                name="password"
                type={showPassword ? 'text' : 'password'}
                value={loginForm.password}
                onChange={handleLoginChange}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              {requires2FA && (
                <TextField
                  fullWidth
                  label={t('auth.2faCode') || 'Código 2FA'}
                  name="totp_code"
                  value={loginForm.totp_code}
                  onChange={handleLoginChange}
                  margin="normal"
                  required
                  placeholder="000000"
                  inputProps={{ maxLength: 6, pattern: '[0-9]*' }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Security />
                      </InputAdornment>
                    ),
                  }}
                  helperText={t('auth.2faHelper') || 'Ingresa el código de tu app de autenticación'}
                />
              )}

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
                <FormControlLabel
                  control={
                    <Checkbox
                      name="rememberMe"
                      checked={loginForm.rememberMe}
                      onChange={handleLoginChange}
                      color="primary"
                    />
                  }
                  label={t('auth.rememberMe') || 'Recordarme'}
                />
                <MuiLink
                  component="button"
                  type="button"
                  variant="body2"
                  onClick={() => setShowPasswordReset(true)}
                  sx={{ cursor: 'pointer' }}
                >
                  {t('auth.forgotPassword') || '¿Olvidaste tu contraseña?'}
                </MuiLink>
              </Box>

              <Button
                fullWidth
                type="submit"
                variant="contained"
                size="large"
                disabled={loading}
                sx={{
                  mt: 3,
                  mb: 2,
                  py: 1.5,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #5568d3 0%, #6a3a8f 100%)',
                  },
                }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : t('auth.login')}
              </Button>
            </form>
          ) : (
            <form onSubmit={handleRegister}>
              <TextField
                fullWidth
                label={t('auth.name')}
                name="name"
                value={registerForm.name}
                onChange={handleRegisterChange}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Person />
                    </InputAdornment>
                  ),
                }}
              />

              <TextField
                fullWidth
                label={t('auth.email')}
                name="email"
                type="email"
                value={registerForm.email}
                onChange={handleRegisterChange}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Email />
                    </InputAdornment>
                  ),
                }}
              />

              <TextField
                fullWidth
                label={t('auth.password')}
                name="password"
                type={showPassword ? 'text' : 'password'}
                value={registerForm.password}
                onChange={handleRegisterChange}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              <TextField
                fullWidth
                label={t('auth.confirmPassword')}
                name="confirmPassword"
                type={showPassword ? 'text' : 'password'}
                value={registerForm.confirmPassword}
                onChange={handleRegisterChange}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock />
                    </InputAdornment>
                  ),
                }}
              />

              <Button
                fullWidth
                type="submit"
                variant="contained"
                size="large"
                disabled={loading}
                sx={{
                  mt: 3,
                  mb: 2,
                  py: 1.5,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #5568d3 0%, #6a3a8f 100%)',
                  },
                }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : t('auth.register')}
              </Button>
            </form>
          )}
        </Paper>
      </Container>

      <Dialog
        open={showPasswordReset}
        onClose={() => !loading && setShowPasswordReset(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {resetStep === 'request' 
            ? (t('auth.resetPassword') || 'Resetear Contraseña')
            : (t('auth.newPassword') || 'Nueva Contraseña')
          }
        </DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
              {error}
            </Alert>
          )}
          {success && (
            <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
              {success}
            </Alert>
          )}

          {resetStep === 'request' ? (
            <TextField
              fullWidth
              label={t('auth.email')}
              type="email"
              value={resetEmail}
              onChange={(e) => setResetEmail(e.target.value)}
              margin="normal"
              required
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Email />
                  </InputAdornment>
                ),
              }}
              helperText={t('auth.resetEmailHelper') || 'Ingresa tu email para recibir instrucciones'}
            />
          ) : (
            <TextField
              fullWidth
              label={t('auth.newPassword')}
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              margin="normal"
              required
              inputProps={{ minLength: 6 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock />
                  </InputAdornment>
                ),
              }}
              helperText={t('auth.passwordMinLength') || 'Mínimo 6 caracteres'}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPasswordReset(false)} disabled={loading}>
            {t('common.cancel') || 'Cancelar'}
          </Button>
          <Button
            onClick={resetStep === 'request' ? handlePasswordResetRequest : handlePasswordResetConfirm}
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={20} /> : (t('common.confirm') || 'Confirmar')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Login;
