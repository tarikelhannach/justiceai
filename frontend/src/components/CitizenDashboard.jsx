import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Alert,
  CircularProgress,
  useTheme,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import {
  Description as DescriptionIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import api from '../services/api';

const CitizenDashboard = () => {
  const { t } = useTranslation();
  const theme = useTheme();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const statuses = [
    { value: 'pending', label: t('cases.status.pending'), color: 'warning' },
    { value: 'in_progress', label: t('cases.status.inProgress'), color: 'info' },
    { value: 'under_review', label: t('cases.status.underReview'), color: 'secondary' },
    { value: 'resolved', label: t('cases.status.resolved'), color: 'success' },
    { value: 'closed', label: t('cases.status.closed'), color: 'default' },
  ];

  const statusSteps = ['pending', 'in_progress', 'under_review', 'resolved', 'closed'];

  const fetchCases = useCallback(async () => {
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
  }, [t]);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  const getStatusColor = (status) => {
    const statusObj = statuses.find(s => s.value === status);
    return statusObj?.color || 'default';
  };

  const getStatusLabel = (status) => {
    const statusObj = statuses.find(s => s.value === status);
    return statusObj?.label || status;
  };

  const getActiveStep = (status) => {
    return statusSteps.indexOf(status);
  };

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
          {t('dashboard.citizen.title')}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {t('dashboard.citizen.subtitle')}
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Statistics */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6}>
          <Card sx={{ bgcolor: theme.palette.primary.main + '15' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.primary.main }}>
                    {cases.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('dashboard.citizen.totalCases')}
                  </Typography>
                </Box>
                <DescriptionIcon sx={{ fontSize: 48, color: theme.palette.primary.main, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Card sx={{ bgcolor: theme.palette.info.main + '15' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.info.main }}>
                    {cases.filter(c => !['resolved', 'closed'].includes(c.status)).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('dashboard.citizen.activeCases')}
                  </Typography>
                </Box>
                <InfoIcon sx={{ fontSize: 48, color: theme.palette.info.main, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Cases */}
      {cases.length === 0 ? (
        <Card>
          <CardContent>
            <Box textAlign="center" py={4}>
              <DescriptionIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                {t('dashboard.citizen.noCases')}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {cases.map((caseItem) => (
            <Grid item xs={12} key={caseItem.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={3}>
                    <Box>
                      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                        {caseItem.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {t('cases.caseNumber')}: {caseItem.case_number}
                      </Typography>
                      {caseItem.description && (
                        <Typography variant="body2" color="text.secondary" mt={1}>
                          {caseItem.description}
                        </Typography>
                      )}
                    </Box>
                    <Chip 
                      label={getStatusLabel(caseItem.status)} 
                      color={getStatusColor(caseItem.status)}
                    />
                  </Box>

                  {caseItem.assigned_judge && (
                    <Box mb={3}>
                      <Typography variant="body2" color="text.secondary">
                        <strong>{t('cases.assignedJudge')}:</strong> {caseItem.assigned_judge.name}
                      </Typography>
                    </Box>
                  )}

                  {/* Case Progress */}
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {t('dashboard.citizen.caseProgress')}
                    </Typography>
                    <Stepper activeStep={getActiveStep(caseItem.status)} alternativeLabel sx={{ mt: 2 }}>
                      {statusSteps.map((step) => (
                        <Step key={step}>
                          <StepLabel>{getStatusLabel(step)}</StepLabel>
                        </Step>
                      ))}
                    </Stepper>
                  </Box>

                  <Box mt={2} display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="caption" color="text.secondary">
                      {t('cases.createdAt')}: {new Date(caseItem.created_at).toLocaleDateString()}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default CitizenDashboard;
