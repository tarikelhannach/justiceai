// frontend/src/components/AdminDashboard.jsx - Dashboard de Administración

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Gavel as GavelIcon,
  Description as DescriptionIcon,
  Security as SecurityIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalCases: 0,
    totalDocuments: 0,
    activeCases: 0,
    pendingDocuments: 0,
    signaturesToday: 0
  });
  
  const [recentActivity, setRecentActivity] = useState([]);
  const [systemHealth, setSystemHealth] = useState('healthy');
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogType, setDialogType] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Actualizar cada 30 segundos
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Obtener estadísticas del sistema
      const statsResponse = await fetch('/api/v1/admin/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }
      
      // Obtener actividad reciente
      const activityResponse = await fetch('/api/v1/admin/activity', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (activityResponse.ok) {
        const activityData = await activityResponse.json();
        setRecentActivity(activityData);
      }
      
      // Obtener estado del sistema
      const healthResponse = await fetch('/api/v1/admin/health');
      
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        setSystemHealth(healthData.status);
      }
      
      // Obtener alertas
      const alertsResponse = await fetch('/api/v1/admin/alerts', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (alertsResponse.ok) {
        const alertsData = await alertsResponse.json();
        setAlerts(alertsData);
      }
      
    } catch (err) {
      setError('Error al cargar datos del dashboard');
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (type) => {
    setDialogType(type);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setDialogType('');
  };

  const handleSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const getHealthColor = (health) => {
    switch (health) {
      case 'healthy': return 'success';
      case 'degraded': return 'warning';
      case 'unhealthy': return 'error';
      default: return 'info';
    }
  };

  const getHealthIcon = (health) => {
    switch (health) {
      case 'healthy': return <CheckCircleIcon />;
      case 'degraded': return <WarningIcon />;
      case 'unhealthy': return <WarningIcon />;
      default: return <WarningIcon />;
    }
  };

  const StatCard = ({ title, value, icon, color = 'primary' }) => (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="h6">
              {title}
            </Typography>
            <Typography variant="h4" component="h2">
              {value}
            </Typography>
          </Box>
          <Box color={`${color}.main`}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Cargando dashboard...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        🏛️ Dashboard de Administración
      </Typography>
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Sistema Judicial Digital - Marruecos
      </Typography>

      {/* Estado del Sistema */}
      <Box mb={3}>
        <Alert 
          severity={getHealthColor(systemHealth)} 
          icon={getHealthIcon(systemHealth)}
          action={
            <Button color="inherit" size="small" onClick={() => fetchDashboardData()}>
              Actualizar
            </Button>
          }
        >
          Estado del Sistema: {systemHealth.toUpperCase()}
        </Alert>
      </Box>

      {/* Estadísticas Principales */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={2}>
          <StatCard
            title="Total Usuarios"
            value={stats.totalUsers}
            icon={<PeopleIcon />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <StatCard
            title="Total Casos"
            value={stats.totalCases}
            icon={<GavelIcon />}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <StatCard
            title="Documentos"
            value={stats.totalDocuments}
            icon={<DescriptionIcon />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <StatCard
            title="Casos Activos"
            value={stats.activeCases}
            icon={<TrendingUpIcon />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <StatCard
            title="Pendientes"
            value={stats.pendingDocuments}
            icon={<WarningIcon />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <StatCard
            title="Firmas Hoy"
            value={stats.signaturesToday}
            icon={<SecurityIcon />}
            color="error"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Actividad Reciente */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Actividad Reciente
              </Typography>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Usuario</TableCell>
                      <TableCell>Acción</TableCell>
                      <TableCell>Recurso</TableCell>
                      <TableCell>Fecha</TableCell>
                      <TableCell>Estado</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentActivity.map((activity, index) => (
                      <TableRow key={index}>
                        <TableCell>{activity.user_email}</TableCell>
                        <TableCell>{activity.action}</TableCell>
                        <TableCell>{activity.resource_type}</TableCell>
                        <TableCell>
                          {new Date(activity.timestamp).toLocaleString('es-ES')}
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={activity.status} 
                            color={activity.status === 'success' ? 'success' : 'error'}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Alertas del Sistema */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Alertas del Sistema
              </Typography>
              <Box>
                {alerts.length === 0 ? (
                  <Typography color="textSecondary">
                    No hay alertas activas
                  </Typography>
                ) : (
                  alerts.map((alert, index) => (
                    <Alert 
                      key={index} 
                      severity={alert.severity} 
                      sx={{ mb: 1 }}
                    >
                      {alert.message}
                    </Alert>
                  ))
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Acciones Rápidas */}
      <Box mt={3}>
        <Typography variant="h6" gutterBottom>
          Acciones Rápidas
        </Typography>
        <Box display="flex" gap={2} flexWrap="wrap">
          <Button 
            variant="contained" 
            startIcon={<PeopleIcon />}
            onClick={() => handleOpenDialog('users')}
          >
            Gestionar Usuarios
          </Button>
          <Button 
            variant="contained" 
            startIcon={<GavelIcon />}
            onClick={() => handleOpenDialog('cases')}
          >
            Gestionar Casos
          </Button>
          <Button 
            variant="contained" 
            startIcon={<SecurityIcon />}
            onClick={() => handleOpenDialog('security')}
          >
            Configuración de Seguridad
          </Button>
          <Button 
            variant="outlined" 
            onClick={() => fetchDashboardData()}
          >
            Actualizar Datos
          </Button>
        </Box>
      </Box>

      {/* Dialog para acciones */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogType === 'users' && 'Gestión de Usuarios'}
          {dialogType === 'cases' && 'Gestión de Casos'}
          {dialogType === 'security' && 'Configuración de Seguridad'}
        </DialogTitle>
        <DialogContent>
          {dialogType === 'users' && (
            <Box>
              <Typography>Funcionalidad de gestión de usuarios en desarrollo...</Typography>
            </Box>
          )}
          {dialogType === 'cases' && (
            <Box>
              <Typography>Funcionalidad de gestión de casos en desarrollo...</Typography>
            </Box>
          )}
          {dialogType === 'security' && (
            <Box>
              <Typography>Funcionalidad de configuración de seguridad en desarrollo...</Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cerrar</Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar para notificaciones */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default AdminDashboard;
