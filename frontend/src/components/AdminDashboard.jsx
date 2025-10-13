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
  Alert,
  alpha,
  useTheme,
  LinearProgress,
} from '@mui/material';
import {
  People as PeopleIcon,
  Gavel as GavelIcon,
  Description as DescriptionIcon,
  Security as SecurityIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';

const AdminDashboard = () => {
  const theme = useTheme();
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalCases: 0,
    totalDocuments: 0,
    activeCases: 0,
    pendingDocuments: 0,
    signaturesToday: 0,
  });

  const [recentActivity, setRecentActivity] = useState([]);
  const [systemHealth, setSystemHealth] = useState('healthy');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Set demo data for now - backend API not yet configured
      setStats({
        totalUsers: 125,
        totalCases: 342,
        totalDocuments: 1567,
        activeCases: 89,
        pendingDocuments: 23,
        signaturesToday: 45,
      });

      setRecentActivity([
        {
          user_email: 'admin@justicia.ma',
          action: 'Crear Caso',
          resource_type: 'Caso Judicial',
          timestamp: new Date().toISOString(),
          status: 'success',
        },
        {
          user_email: 'juez@justicia.ma',
          action: 'Firmar Documento',
          resource_type: 'Documento',
          timestamp: new Date(Date.now() - 300000).toISOString(),
          status: 'success',
        },
        {
          user_email: 'secretario@justicia.ma',
          action: 'Actualizar Caso',
          resource_type: 'Caso Judicial',
          timestamp: new Date(Date.now() - 600000).toISOString(),
          status: 'success',
        },
      ]);

      setSystemHealth('healthy');
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon: Icon, color = 'primary', trend }) => (
    <Card
      sx={{
        position: 'relative',
        overflow: 'visible',
        background: alpha(theme.palette[color].main, 0.05),
        border: `1px solid ${alpha(theme.palette[color].main, 0.1)}`,
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          background: `linear-gradient(90deg, ${theme.palette[color].main}, ${theme.palette[color].light})`,
          borderRadius: '16px 16px 0 0',
        },
      }}
    >
      <CardContent sx={{ pt: 3 }}>
        <Box display="flex" alignItems="flex-start" justifyContent="space-between">
          <Box sx={{ flex: 1 }}>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mb: 1, fontWeight: 500 }}
            >
              {title}
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
              {loading ? '...' : value.toLocaleString()}
            </Typography>
            {trend && (
              <Box display="flex" alignItems="center" gap={0.5}>
                <TrendingUpIcon fontSize="small" color={color} />
                <Typography variant="caption" color={`${color}.main`} fontWeight={600}>
                  +{trend}% este mes
                </Typography>
              </Box>
            )}
          </Box>
          <Box
            sx={{
              bgcolor: alpha(theme.palette[color].main, 0.1),
              borderRadius: 3,
              p: 1.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Icon sx={{ fontSize: 32, color: theme.palette[color].main }} />
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
          Dashboard de Administración
        </Typography>
        <LinearProgress sx={{ mt: 2, borderRadius: 1 }} />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
          Dashboard de Administración
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Bienvenido al Sistema Judicial Digital de Marruecos 🇲🇦
        </Typography>
      </Box>

      {/* Estado del Sistema */}
      <Box mb={4}>
        <Alert
          severity="success"
          icon={<CheckCircleIcon />}
          sx={{
            borderRadius: 2,
            border: `1px solid ${alpha(theme.palette.success.main, 0.2)}`,
          }}
          action={
            <Button
              color="inherit"
              size="small"
              onClick={() => fetchDashboardData()}
              sx={{ fontWeight: 600 }}
            >
              Actualizar
            </Button>
          }
        >
          <Typography variant="body2" fontWeight={600}>
            Sistema Operativo - Todos los servicios funcionando correctamente
          </Typography>
        </Alert>
      </Box>

      {/* Estadísticas Principales */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Usuarios"
            value={stats.totalUsers}
            icon={PeopleIcon}
            color="primary"
            trend={12}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Casos"
            value={stats.totalCases}
            icon={GavelIcon}
            color="secondary"
            trend={8}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Documentos"
            value={stats.totalDocuments}
            icon={DescriptionIcon}
            color="info"
            trend={15}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Casos Activos"
            value={stats.activeCases}
            icon={TrendingUpIcon}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Pendientes"
            value={stats.pendingDocuments}
            icon={WarningIcon}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Firmas Hoy"
            value={stats.signaturesToday}
            icon={SecurityIcon}
            color="error"
          />
        </Grid>
      </Grid>

      {/* Actividad Reciente */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
            Actividad Reciente
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>Usuario</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Acción</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Recurso</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Fecha</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Estado</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recentActivity.map((activity, index) => (
                  <TableRow
                    key={index}
                    sx={{
                      '&:hover': {
                        bgcolor: alpha(theme.palette.primary.main, 0.05),
                      },
                    }}
                  >
                    <TableCell>{activity.user_email}</TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight={500}>
                        {activity.action}
                      </Typography>
                    </TableCell>
                    <TableCell>{activity.resource_type}</TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {new Date(activity.timestamp).toLocaleString('es-ES')}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={activity.status}
                        color={activity.status === 'success' ? 'success' : 'error'}
                        size="small"
                        sx={{ fontWeight: 600 }}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Acciones Rápidas */}
      <Card
        sx={{
          background: theme.palette.background.gradient,
          color: 'white',
        }}
      >
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            Acciones Rápidas
          </Typography>
          <Box display="flex" gap={2} flexWrap="wrap" mt={2}>
            <Button
              variant="contained"
              sx={{
                bgcolor: 'white',
                color: theme.palette.primary.main,
                '&:hover': {
                  bgcolor: alpha('#ffffff', 0.9),
                },
              }}
              startIcon={<GavelIcon />}
            >
              Nuevo Caso
            </Button>
            <Button
              variant="outlined"
              sx={{
                borderColor: 'white',
                color: 'white',
                '&:hover': {
                  borderColor: 'white',
                  bgcolor: alpha('#ffffff', 0.1),
                },
              }}
              startIcon={<DescriptionIcon />}
            >
              Subir Documento
            </Button>
            <Button
              variant="outlined"
              sx={{
                borderColor: 'white',
                color: 'white',
                '&:hover': {
                  borderColor: 'white',
                  bgcolor: alpha('#ffffff', 0.1),
                },
              }}
              startIcon={<PeopleIcon />}
            >
              Gestionar Usuarios
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AdminDashboard;
