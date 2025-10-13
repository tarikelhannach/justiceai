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
  HourglassEmpty as PendingIcon,
} from '@mui/icons-material';
import { casesAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

const AdminDashboard = () => {
  const theme = useTheme();
  const { user } = useAuth();
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    in_progress: 0,
    resolved: 0,
    closed: 0,
  });

  const [recentCases, setRecentCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Obtener estadísticas reales del backend
      const caseStats = await casesAPI.getCaseStats();
      setStats(caseStats);

      // Obtener casos recientes
      const cases = await casesAPI.getCases({ skip: 0, limit: 5 });
      setRecentCases(cases);

    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.response?.data?.detail || 'Error al cargar datos del dashboard');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'warning',
      in_progress: 'info',
      resolved: 'success',
      closed: 'secondary',
      archived: 'secondary',
    };
    return colors[status] || 'primary';
  };

  const getStatusLabel = (status) => {
    const labels = {
      pending: 'Pendiente',
      in_progress: 'En Progreso',
      resolved: 'Resuelto',
      closed: 'Cerrado',
      archived: 'Archivado',
    };
    return labels[status] || status;
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
                  {trend}
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

  if (loading && stats.total === 0) {
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
          Bienvenido {user?.name} - {user?.role === 'admin' ? 'Administrador' : user?.role} 🇲🇦
        </Typography>
      </Box>

      {/* Error Alert */}
      {error && (
        <Box mb={4}>
          <Alert severity="error" onClose={() => setError(null)} sx={{ borderRadius: 2 }}>
            {error}
          </Alert>
        </Box>
      )}

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
              disabled={loading}
              sx={{ fontWeight: 600 }}
            >
              Actualizar
            </Button>
          }
        >
          <Typography variant="body2" fontWeight={600}>
            Sistema Operativo - Base de datos conectada
          </Typography>
        </Alert>
      </Box>

      {/* Estadísticas Principales */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total de Casos"
            value={stats.total}
            icon={GavelIcon}
            color="primary"
            trend={`${stats.total} casos en el sistema`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Casos Pendientes"
            value={stats.pending}
            icon={PendingIcon}
            color="warning"
            trend={`${stats.pending} esperando asignación`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="En Progreso"
            value={stats.in_progress}
            icon={TrendingUpIcon}
            color="info"
            trend={`${stats.in_progress} activos`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Casos Resueltos"
            value={stats.resolved}
            icon={CheckCircleIcon}
            color="success"
            trend={`${stats.resolved} completados`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Casos Cerrados"
            value={stats.closed}
            icon={SecurityIcon}
            color="secondary"
            trend={`${stats.closed} archivados`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Tasa de Resolución"
            value={stats.total > 0 ? Math.round((stats.resolved / stats.total) * 100) : 0}
            icon={DescriptionIcon}
            color="secondary"
            trend={`${stats.total > 0 ? Math.round((stats.resolved / stats.total) * 100) : 0}% completado`}
          />
        </Grid>
      </Grid>

      {/* Casos Recientes */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
            Casos Recientes
          </Typography>
          {recentCases.length === 0 ? (
            <Typography color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
              No hay casos disponibles
            </Typography>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Número</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Título</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Propietario</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Juez Asignado</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Estado</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Fecha</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentCases.map((caseItem) => (
                    <TableRow
                      key={caseItem.id}
                      sx={{
                        '&:hover': {
                          bgcolor: alpha(theme.palette.primary.main, 0.05),
                        },
                      }}
                    >
                      <TableCell>
                        <Typography variant="body2" fontWeight={600}>
                          {caseItem.case_number}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {caseItem.title}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {caseItem.owner?.name || 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {caseItem.assigned_judge?.name || 'Sin asignar'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={getStatusLabel(caseItem.status)}
                          color={getStatusColor(caseItem.status)}
                          size="small"
                          sx={{ fontWeight: 600 }}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {new Date(caseItem.created_at).toLocaleDateString('es-ES')}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
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
