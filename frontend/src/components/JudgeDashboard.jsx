import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Alert,
  CircularProgress,
  useTheme,
} from '@mui/material';
import {
  Gavel as GavelIcon,
  Description as DescriptionIcon,
  CheckCircle as CheckCircleIcon,
  Update as UpdateIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import api from '../services/api';
import { usePermissions } from '../hooks/usePermissions';

const JudgeDashboard = () => {
  const { t } = useTranslation();
  const theme = useTheme();
  const { user, canChangeCaseStatus } = usePermissions();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCase, setSelectedCase] = useState(null);
  const [statusDialogOpen, setStatusDialogOpen] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [updating, setUpdating] = useState(false);

  const statuses = [
    { value: 'pending', label: t('cases.status.pending'), color: 'warning' },
    { value: 'in_progress', label: t('cases.status.inProgress'), color: 'info' },
    { value: 'under_review', label: t('cases.status.underReview'), color: 'secondary' },
    { value: 'resolved', label: t('cases.status.resolved'), color: 'success' },
    { value: 'closed', label: t('cases.status.closed'), color: 'default' },
  ];

  useEffect(() => {
    fetchCases();
  }, []);

  const fetchCases = async () => {
    try {
      setLoading(true);
      const response = await api.get('/cases/');
      setCases(response.data);
      setError(null);
    } catch (err) {
      setError(t('common.error') + ': ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleOpenStatusDialog = (caseData) => {
    setSelectedCase(caseData);
    setNewStatus(caseData.status);
    setStatusDialogOpen(true);
  };

  const handleCloseStatusDialog = () => {
    setStatusDialogOpen(false);
    setSelectedCase(null);
    setNewStatus('');
  };

  const handleUpdateStatus = async () => {
    if (!selectedCase || !newStatus) return;

    try {
      setUpdating(true);
      await api.put(`/cases/${selectedCase.id}`, {
        status: newStatus,
      });
      await fetchCases();
      handleCloseStatusDialog();
    } catch (err) {
      setError(t('common.error') + ': ' + (err.response?.data?.detail || err.message));
    } finally {
      setUpdating(false);
    }
  };

  const getStatusColor = (status) => {
    const statusObj = statuses.find(s => s.value === status);
    return statusObj?.color || 'default';
  };

  const getStatusLabel = (status) => {
    const statusObj = statuses.find(s => s.value === status);
    return statusObj?.label || status;
  };

  const pendingCases = cases.filter(c => c.status === 'pending').length;
  const inProgressCases = cases.filter(c => c.status === 'in_progress').length;
  const resolvedCases = cases.filter(c => c.status === 'resolved').length;

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
          {t('dashboard.judge.title')}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {t('dashboard.judge.subtitle')}
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Statistics */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: theme.palette.warning.main + '15' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.warning.main }}>
                    {pendingCases}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('cases.status.pending')}
                  </Typography>
                </Box>
                <GavelIcon sx={{ fontSize: 48, color: theme.palette.warning.main, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: theme.palette.info.main + '15' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.info.main }}>
                    {inProgressCases}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('cases.status.inProgress')}
                  </Typography>
                </Box>
                <UpdateIcon sx={{ fontSize: 48, color: theme.palette.info.main, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: theme.palette.success.main + '15' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.success.main }}>
                    {resolvedCases}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('cases.status.resolved')}
                  </Typography>
                </Box>
                <CheckCircleIcon sx={{ fontSize: 48, color: theme.palette.success.main, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: theme.palette.primary.main + '15' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.primary.main }}>
                    {cases.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('dashboard.judge.totalAssigned')}
                  </Typography>
                </Box>
                <DescriptionIcon sx={{ fontSize: 48, color: theme.palette.primary.main, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Cases Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
            {t('dashboard.judge.assignedCases')}
          </Typography>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>{t('cases.caseNumber')}</strong></TableCell>
                  <TableCell><strong>{t('cases.title')}</strong></TableCell>
                  <TableCell><strong>{t('cases.owner')}</strong></TableCell>
                  <TableCell><strong>{t('cases.status.title')}</strong></TableCell>
                  <TableCell><strong>{t('cases.createdAt')}</strong></TableCell>
                  <TableCell align="center"><strong>{t('common.actions')}</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {cases.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography variant="body2" color="text.secondary" py={3}>
                        {t('dashboard.judge.noCases')}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  cases.map((caseItem) => (
                    <TableRow key={caseItem.id} hover>
                      <TableCell>{caseItem.case_number}</TableCell>
                      <TableCell>{caseItem.title}</TableCell>
                      <TableCell>{caseItem.owner?.name || '-'}</TableCell>
                      <TableCell>
                        <Chip 
                          label={getStatusLabel(caseItem.status)} 
                          color={getStatusColor(caseItem.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(caseItem.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell align="center">
                        {canChangeCaseStatus(caseItem) && (
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => handleOpenStatusDialog(caseItem)}
                          >
                            {t('cases.changeStatus')}
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Status Change Dialog */}
      <Dialog open={statusDialogOpen} onClose={handleCloseStatusDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{t('cases.changeStatus')}</DialogTitle>
        <DialogContent>
          <Box mt={2}>
            <TextField
              select
              fullWidth
              label={t('cases.status.title')}
              value={newStatus}
              onChange={(e) => setNewStatus(e.target.value)}
            >
              {statuses.map((status) => (
                <MenuItem key={status.value} value={status.value}>
                  {status.label}
                </MenuItem>
              ))}
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseStatusDialog}>{t('common.cancel')}</Button>
          <Button 
            onClick={handleUpdateStatus} 
            variant="contained" 
            disabled={updating || !newStatus}
          >
            {updating ? <CircularProgress size={20} /> : t('common.save')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default JudgeDashboard;
