// frontend/src/components/TwoFactorSetup.js - Configuración de 2FA

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Security,
  QrCode,
  Phone,
  Backup,
  CheckCircle,
  Warning,
} from '@mui/icons-material';
import axios from 'axios';
import toast from 'react-hot-toast';

const TwoFactorSetup = () => {
  const [step, setStep] = useState(0);
  const [qrCode, setQrCode] = useState('');
  const [secret, setSecret] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [backupCodes, setBackupCodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showBackupCodes, setShowBackupCodes] = useState(false);

  const steps = [
    'Configurar 2FA',
    'Verificar Código',
    'Códigos de Respaldo',
  ];

  useEffect(() => {
    generateSecret();
  }, []);

  const generateSecret = async () => {
    try {
      setLoading(true);
      const response = await axios.post('/api/v1/auth/2fa/setup');
      setSecret(response.data.secret);
      setQrCode(response.data.qr_code);
      setStep(1);
    } catch (error) {
      setError('Error al generar clave secreta');
      toast.error('Error al configurar 2FA');
    } finally {
      setLoading(false);
    }
  };

  const verifyCode = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      setError('Por favor ingrese un código de 6 dígitos');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post('/api/v1/auth/2fa/verify', {
        secret,
        code: verificationCode,
      });

      if (response.data.verified) {
        setSuccess('2FA configurado exitosamente');
        generateBackupCodes();
        setStep(2);
      } else {
        setError('Código de verificación inválido');
      }
    } catch (error) {
      setError('Error al verificar código');
      toast.error('Error al verificar código');
    } finally {
      setLoading(false);
    }
  };

  const generateBackupCodes = async () => {
    try {
      const response = await axios.post('/api/v1/auth/2fa/backup-codes');
      setBackupCodes(response.data.codes);
      setShowBackupCodes(true);
    } catch (error) {
      console.error('Error generating backup codes:', error);
    }
  };

  const downloadBackupCodes = () => {
    const codesText = backupCodes.join('\n');
    const blob = new Blob([codesText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = '2fa-backup-codes.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const renderStepContent = () => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="h5" gutterBottom>
              Configurar Autenticación de Dos Factores
            </Typography>
            
            <Paper sx={{ p: 2, mt: 2, mb: 2 }}>
              <Typography variant="body2" color="textSecondary">
                La autenticación de dos factores (2FA) añade una capa adicional de seguridad 
                a su cuenta. Necesitará una aplicación autenticadora como Google Authenticator 
                o Authy.
              </Typography>
            </Paper>

            <List>
              <ListItem>
                <ListItemIcon>
                  <Security color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary="Mayor Seguridad"
                  secondary="Protege su cuenta incluso si su contraseña es comprometida"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <QrCode color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary="Fácil Configuración"
                  secondary="Escanee un código QR con su aplicación autenticadora"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Backup color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary="Códigos de Respaldo"
                  secondary="Reciba códigos de respaldo para casos de emergencia"
                />
              </ListItem>
            </List>

            <Button
              variant="contained"
              onClick={generateSecret}
              disabled={loading}
              sx={{ mt: 2 }}
            >
              {loading ? 'Generando...' : 'Configurar 2FA'}
            </Button>
          </Box>
        );

      case 1:
        return (
          <Box>
            <Typography variant="h5" gutterBottom>
              Escanear Código QR
            </Typography>
            
            <Paper sx={{ p: 2, mt: 2, mb: 2 }}>
              <Typography variant="body2" color="textSecondary">
                1. Abra su aplicación autenticadora (Google Authenticator, Authy, etc.)
                <br />
                2. Escanee el código QR que aparece abajo
                <br />
                3. Ingrese el código de 6 dígitos generado por la aplicación
              </Typography>
            </Paper>

            {qrCode && (
              <Box sx={{ textAlign: 'center', mb: 2 }}>
                <img
                  src={qrCode}
                  alt="QR Code for 2FA"
                  style={{ maxWidth: '200px', height: 'auto' }}
                />
              </Box>
            )}

            <TextField
              fullWidth
              label="Código de Verificación"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
              placeholder="123456"
              inputProps={{ maxLength: 6 }}
              sx={{ mb: 2 }}
            />

            <Button
              variant="contained"
              onClick={verifyCode}
              disabled={loading || !verificationCode}
              fullWidth
            >
              {loading ? 'Verificando...' : 'Verificar Código'}
            </Button>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Box>
        );

      case 2:
        return (
          <Box>
            <Typography variant="h5" gutterBottom>
              Configuración Completada
            </Typography>
            
            <Alert severity="success" sx={{ mb: 2 }}>
              <Typography variant="h6">
                ¡2FA configurado exitosamente!
              </Typography>
              Su cuenta ahora está protegida con autenticación de dos factores.
            </Alert>

            <Paper sx={{ p: 2, mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                Códigos de Respaldo
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                Guarde estos códigos en un lugar seguro. Pueden usarse para acceder 
                a su cuenta si pierde su dispositivo autenticador.
              </Typography>
              
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                {backupCodes.map((code, index) => (
                  <Chip
                    key={index}
                    label={code}
                    variant="outlined"
                    size="small"
                  />
                ))}
              </Box>
              
              <Button
                variant="outlined"
                onClick={downloadBackupCodes}
                startIcon={<Backup />}
              >
                Descargar Códigos
              </Button>
            </Paper>

            <Button
              variant="contained"
              onClick={() => window.location.href = '/dashboard'}
              fullWidth
            >
              Ir al Dashboard
            </Button>
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 2 }}>
      <Card>
        <CardContent>
          <Stepper activeStep={step} sx={{ mb: 3 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
          
          <Divider sx={{ mb: 3 }} />
          
          {renderStepContent()}
        </CardContent>
      </Card>

      {/* Dialog para mostrar códigos de respaldo */}
      <Dialog
        open={showBackupCodes}
        onClose={() => setShowBackupCodes(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Códigos de Respaldo - ¡Guárdelos Seguros!
        </DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="body2">
              Estos códigos son únicos y solo se muestran una vez. 
              Guárdelos en un lugar seguro.
            </Typography>
          </Alert>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {backupCodes.map((code, index) => (
              <Chip
                key={index}
                label={code}
                variant="outlined"
                size="small"
              />
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={downloadBackupCodes}>
            Descargar
          </Button>
          <Button onClick={() => setShowBackupCodes(false)} variant="contained">
            Entendido
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TwoFactorSetup;
