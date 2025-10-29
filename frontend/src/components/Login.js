// frontend/src/components/Login.js - Componente de Login con 2FA

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Divider,
  InputAdornment,
  IconButton,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Security,
  QrCode,
  Email,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const { login } = useAuth();
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    twoFactorCode: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const steps = [
    'Credenciales',
    'Autenticación de Dos Factores',
  ];

  const handleInputChange = (field) => (event) => {
    setFormData({
      ...formData,
      [field]: event.target.value,
    });
    setError('');
  };

  const handleLogin = async () => {
    if (!formData.email || !formData.password) {
      setError('Por favor complete todos los campos');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await login(formData.email, formData.password);
      
      if (result.success) {
        // Login exitoso
        return;
      } else if (result.requires2FA || result.error?.includes('2FA')) {
        // Requiere 2FA
        setStep(1);
        if (result.error && !result.error.includes('2FA')) {
          setError(result.error);
        }
      } else {
        setError(result.error);
      }
    } catch (error) {
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const handle2FA = async () => {
    if (!formData.twoFactorCode) {
      setError('Por favor ingrese el código de verificación');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await login(
        formData.email,
        formData.password,
        formData.twoFactorCode
      );
      
      if (!result.success) {
        setError(result.error);
      }
    } catch (error) {
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setStep(0);
    setFormData({
      ...formData,
      twoFactorCode: '',
    });
    setError('');
  };

  const renderStepContent = () => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="h4" gutterBottom align="center">
              🏛️ Sistema Judicial Digital
            </Typography>
            <Typography variant="h6" gutterBottom align="center" color="textSecondary">
              Reino de Marruecos
            </Typography>
            
            <Box sx={{ mt: 3 }}>
              <TextField
                fullWidth
                label="Correo Electrónico"
                type="email"
                value={formData.email}
                onChange={handleInputChange('email')}
                margin="normal"
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
                label="Contraseña"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleInputChange('password')}
                margin="normal"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Security />
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
              
              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}
              
              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handleLogin}
                disabled={loading}
                sx={{ mt: 3 }}
              >
                {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
              </Button>
            </Box>
          </Box>
        );

      case 1:
        return (
          <Box>
            <Typography variant="h5" gutterBottom align="center">
              Autenticación de Dos Factores
            </Typography>
            
            <Paper sx={{ p: 2, mt: 2, mb: 2 }}>
              <Typography variant="body2" color="textSecondary">
                Por seguridad, se requiere verificación adicional. Ingrese el código de 6 dígitos 
                de su aplicación autenticadora o el código SMS enviado a su teléfono.
              </Typography>
            </Paper>
            
            <TextField
              fullWidth
              label="Código de Verificación"
              value={formData.twoFactorCode}
              onChange={handleInputChange('twoFactorCode')}
              margin="normal"
              placeholder="123456"
              inputProps={{ maxLength: 6 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <QrCode />
                  </InputAdornment>
                ),
              }}
            />
            
            <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
              <Button
                variant="outlined"
                onClick={handleBack}
                disabled={loading}
                sx={{ flex: 1 }}
              >
                Atrás
              </Button>
              <Button
                variant="contained"
                onClick={handle2FA}
                disabled={loading || !formData.twoFactorCode}
                sx={{ flex: 1 }}
              >
                {loading ? 'Verificando...' : 'Verificar'}
              </Button>
            </Box>
            
            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        p: 2,
      }}
    >
      <Card sx={{ maxWidth: 500, width: '100%' }}>
        <CardContent sx={{ p: 4 }}>
          <Stepper activeStep={step} sx={{ mb: 3 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
          
          <Divider sx={{ mb: 3 }} />
          
          {renderStepContent()}
          
          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Typography variant="body2" color="textSecondary">
              ¿Problemas para acceder? Contacte al administrador del sistema
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Login;
