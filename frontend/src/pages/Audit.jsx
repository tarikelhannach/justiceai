// frontend/src/pages/Audit.jsx - Dashboard de Auditoría

import { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  IconButton,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  FilterList as FilterIcon,
  Visibility as VisibilityIcon,
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
  Assignment as AssignmentIcon
} from '@mui/icons-material';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#a5d8ff'];

export default function Audit() {
  const { t } = useTranslation();
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [totalLogs, setTotalLogs] = useState(0);
  const [selectedLog, setSelectedLog] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  
  // Filtros
  const [filters, setFilters] = useState({
    action: '',
    resource_type: '',
    user_id: '',
    status: '',
    search: '',
    start_date: '',
    end_date: ''
  });

  const [actions, setActions] = useState([]);
  const [resourceTypes, setResourceTypes] = useState([]);

  // Cargar datos SOLO cuando cambien page o rowsPerPage (NO filters)
  useEffect(() => {
    loadAuditLogs();
  }, [page, rowsPerPage]);

  // Cuando cambien filters: resetear página Y recargar datos
  useEffect(() => {
    if (page === 0) {
      // Si ya estamos en página 0, recargar directamente
      loadAuditLogs();
      loadStats();
    } else {
      // Si no, resetear página (esto disparará el effect anterior)
      setPage(0);
      loadStats();
    }
  }, [filters]);

  // Cargar filtros disponibles y stats solo al inicio
  useEffect(() => {
    loadFilters();
    loadStats();
  }, []);

  const loadAuditLogs = async () => {
    try {
      setLoading(true);
      
      // Cancelar request anterior si existe
      if (window.auditLogsAbortController) {
        window.auditLogsAbortController.abort();
      }
      
      // Crear nuevo AbortController para este request
      const abortController = new AbortController();
      window.auditLogsAbortController = abortController;
      
      const params = {
        skip: page * rowsPerPage,
        limit: rowsPerPage,
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== ''))
      };

      const response = await axios.get('/api/audit/logs', { 
        params,
        signal: abortController.signal 
      });
      
      setLogs(response.data.logs || response.data);
      // Usar nullish coalescing para manejar correctamente total = 0
      setTotalLogs(response.data.total !== undefined ? response.data.total : response.data.length);
    } catch (error) {
      if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
        // Request cancelado, ignorar error
        return;
      }
      console.error('Error loading audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get('/api/audit/stats', {
        params: { days: 30 }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const loadFilters = async () => {
    try {
      const [actionsRes, resourceTypesRes] = await Promise.all([
        axios.get('/api/audit/actions'),
        axios.get('/api/audit/resource-types')
      ]);
      setActions(actionsRes.data);
      setResourceTypes(resourceTypesRes.data);
    } catch (error) {
      console.error('Error loading filters:', error);
    }
  };

  const handleExport = async (format) => {
    try {
      const params = {
        format,
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== ''))
      };

      const response = await axios.get('/api/audit/export', {
        params,
        responseType: format === 'csv' ? 'blob' : 'json'
      });

      if (format === 'csv') {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `audit_logs_${new Date().toISOString()}.csv`);
        document.body.appendChild(link);
        link.click();
        link.remove();
      } else {
        const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `audit_logs_${new Date().toISOString()}.json`);
        document.body.appendChild(link);
        link.click();
        link.remove();
      }
    } catch (error) {
      console.error('Error exporting logs:', error);
    }
  };

  const handleViewDetails = (log) => {
    setSelectedLog(log);
    setDetailsOpen(true);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'success';
      case 'failure': return 'error';
      case 'warning': return 'warning';
      default: return 'default';
    }
  };

  const formatDate = (date) => {
    return new Date(date).toLocaleString('es-ES');
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">{t('audit.title', 'Auditoría del Sistema')}</Typography>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => { loadAuditLogs(); loadStats(); }}
          >
            {t('audit.refresh', 'Actualizar')}
          </Button>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={() => handleExport('json')}
          >
            {t('audit.export_json', 'Exportar JSON')}
          </Button>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={() => handleExport('csv')}
          >
            {t('audit.export_csv', 'Exportar CSV')}
          </Button>
        </Stack>
      </Box>

      {/* Statistics Cards */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Stack direction="row" spacing={2} alignItems="center">
                  <AssignmentIcon color="primary" sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h4">{stats.total_logs}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {t('audit.total_logs', 'Total Logs')} ({stats.days} días)
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Stack direction="row" spacing={2} alignItems="center">
                  <SecurityIcon color="success" sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h4">
                      {stats.by_status.find(s => s.status === 'success')?.count || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {t('audit.successful', 'Exitosos')}
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Stack direction="row" spacing={2} alignItems="center">
                  <TrendingUpIcon color="warning" sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h4">
                      {stats.by_status.find(s => s.status === 'failure')?.count || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {t('audit.failures', 'Fallidos')}
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Stack direction="row" spacing={2} alignItems="center">
                  <FilterIcon color="info" sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h4">{stats.by_action.length}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {t('audit.action_types', 'Tipos de Acción')}
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Charts */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>{t('audit.by_action', 'Por Acción')}</Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={stats.by_action}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="action" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>{t('audit.by_status', 'Por Estado')}</Typography>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={stats.by_status}
                    dataKey="count"
                    nameKey="status"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label
                  >
                    {stats.by_status.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>{t('audit.timeline', 'Línea de Tiempo')}</Typography>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={stats.by_day}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="count" stroke="#8884d8" name={t('audit.logs', 'Logs')} />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>{t('audit.filters', 'Filtros')}</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>{t('audit.action', 'Acción')}</InputLabel>
              <Select
                value={filters.action}
                label={t('audit.action', 'Acción')}
                onChange={(e) => setFilters({ ...filters, action: e.target.value })}
              >
                <MenuItem value="">{t('audit.all', 'Todas')}</MenuItem>
                {actions.map(action => (
                  <MenuItem key={action} value={action}>{action}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>{t('audit.resource_type', 'Tipo de Recurso')}</InputLabel>
              <Select
                value={filters.resource_type}
                label={t('audit.resource_type', 'Tipo de Recurso')}
                onChange={(e) => setFilters({ ...filters, resource_type: e.target.value })}
              >
                <MenuItem value="">{t('audit.all', 'Todos')}</MenuItem>
                {resourceTypes.map(type => (
                  <MenuItem key={type} value={type}>{type}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>{t('audit.status', 'Estado')}</InputLabel>
              <Select
                value={filters.status}
                label={t('audit.status', 'Estado')}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              >
                <MenuItem value="">{t('audit.all', 'Todos')}</MenuItem>
                <MenuItem value="success">{t('audit.success', 'Exitoso')}</MenuItem>
                <MenuItem value="failure">{t('audit.failure', 'Fallido')}</MenuItem>
                <MenuItem value="warning">{t('audit.warning', 'Advertencia')}</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label={t('audit.search', 'Buscar')}
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              placeholder={t('audit.search_placeholder', 'IP, acción, detalles...')}
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Audit Logs Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{t('audit.timestamp', 'Fecha/Hora')}</TableCell>
              <TableCell>{t('audit.user', 'Usuario')}</TableCell>
              <TableCell>{t('audit.action', 'Acción')}</TableCell>
              <TableCell>{t('audit.resource', 'Recurso')}</TableCell>
              <TableCell>{t('audit.status', 'Estado')}</TableCell>
              <TableCell>{t('audit.ip', 'IP')}</TableCell>
              <TableCell align="center">{t('audit.actions', 'Acciones')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {logs.map((log) => (
              <TableRow key={log.id} hover>
                <TableCell>{formatDate(log.created_at)}</TableCell>
                <TableCell>{log.user?.name || `ID: ${log.user_id}`}</TableCell>
                <TableCell>
                  <Chip label={log.action} size="small" color="primary" variant="outlined" />
                </TableCell>
                <TableCell>
                  {log.resource_type && (
                    <Chip label={`${log.resource_type} #${log.resource_id}`} size="small" />
                  )}
                </TableCell>
                <TableCell>
                  <Chip
                    label={log.status}
                    size="small"
                    color={getStatusColor(log.status)}
                  />
                </TableCell>
                <TableCell>{log.ip_address}</TableCell>
                <TableCell align="center">
                  <IconButton
                    size="small"
                    onClick={() => handleViewDetails(log)}
                    color="primary"
                  >
                    <VisibilityIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        <TablePagination
          rowsPerPageOptions={[25, 50, 100]}
          component="div"
          count={totalLogs}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(e, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </TableContainer>

      {/* Details Dialog */}
      <Dialog open={detailsOpen} onClose={() => setDetailsOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>{t('audit.log_details', 'Detalles del Log')}</DialogTitle>
        <DialogContent>
          {selectedLog && (
            <Box sx={{ pt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">ID</Typography>
                  <Typography variant="body1">{selectedLog.id}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">{t('audit.timestamp', 'Fecha/Hora')}</Typography>
                  <Typography variant="body1">{formatDate(selectedLog.created_at)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">{t('audit.user', 'Usuario')}</Typography>
                  <Typography variant="body1">{selectedLog.user?.name || `ID: ${selectedLog.user_id}`}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">{t('audit.action', 'Acción')}</Typography>
                  <Typography variant="body1">{selectedLog.action}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">{t('audit.resource', 'Recurso')}</Typography>
                  <Typography variant="body1">
                    {selectedLog.resource_type} #{selectedLog.resource_id}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">{t('audit.status', 'Estado')}</Typography>
                  <Chip label={selectedLog.status} color={getStatusColor(selectedLog.status)} />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">{t('audit.ip', 'IP')}</Typography>
                  <Typography variant="body1">{selectedLog.ip_address}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">{t('audit.user_agent', 'User Agent')}</Typography>
                  <Typography variant="body1" sx={{ wordBreak: 'break-word' }}>
                    {selectedLog.user_agent}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">{t('audit.details', 'Detalles')}</Typography>
                  <Paper variant="outlined" sx={{ p: 2, mt: 1, bgcolor: 'grey.50' }}>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {selectedLog.details || t('audit.no_details', 'Sin detalles')}
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>{t('common.close', 'Cerrar')}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
