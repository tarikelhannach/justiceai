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
  Alert,
  CircularProgress,
  useTheme,
  IconButton,
} from '@mui/material';
import {
  Add as AddIcon,
  Description as DescriptionIcon,
  AttachFile as AttachFileIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import api from '../services/api';
import DocumentUpload from './DocumentUpload';

const LawyerDashboard = () => {
  const { t } = useTranslation();
  const theme = useTheme();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedCase, setSelectedCase] = useState(null);

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

  const handleOpenUploadDialog = (caseData) => {
    setSelectedCase(caseData);
    setUploadDialogOpen(true);
  };

  const handleCloseUploadDialog = () => {
    setUploadDialogOpen(false);
    setSelectedCase(null);
  };

  const handleUploadSuccess = () => {
    handleCloseUploadDialog();
    fetchCases();
  };

  const getStatusColor = (status) => {
    const statusObj = statuses.find(s => s.value === status);
    return statusObj?.color || 'default';
  };

  const getStatusLabel = (status) => {
    const statusObj = statuses.find(s => s.value === status);
    return statusObj?.label || status;
  };

  const activeCases = cases.filter(c => !['resolved', 'closed'].includes(c.status)).length;

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
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
            {t('dashboard.lawyer.title')}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {t('dashboard.lawyer.subtitle')}
          </Typography>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Statistics */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ bgcolor: theme.palette.primary.main + '15' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.primary.main }}>
                    {cases.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('dashboard.lawyer.totalCases')}
                  </Typography>
                </Box>
                <DescriptionIcon sx={{ fontSize: 48, color: theme.palette.primary.main, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ bgcolor: theme.palette.info.main + '15' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.info.main }}>
                    {activeCases}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('dashboard.lawyer.activeCases')}
                  </Typography>
                </Box>
                <AttachFileIcon sx={{ fontSize: 48, color: theme.palette.info.main, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Cases Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
            {t('dashboard.lawyer.myCases')}
          </Typography>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>{t('cases.caseNumber')}</strong></TableCell>
                  <TableCell><strong>{t('cases.title')}</strong></TableCell>
                  <TableCell><strong>{t('cases.assignedJudge')}</strong></TableCell>
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
                        {t('dashboard.lawyer.noCases')}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  cases.map((caseItem) => (
                    <TableRow key={caseItem.id} hover>
                      <TableCell>{caseItem.case_number}</TableCell>
                      <TableCell>{caseItem.title}</TableCell>
                      <TableCell>{caseItem.assigned_judge?.name || t('cases.notAssigned')}</TableCell>
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
                        <IconButton 
                          size="small" 
                          color="primary"
                          onClick={() => handleOpenUploadDialog(caseItem)}
                          title={t('documents.upload')}
                        >
                          <AttachFileIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Document Upload Dialog */}
      {selectedCase && (
        <DocumentUpload
          open={uploadDialogOpen}
          onClose={handleCloseUploadDialog}
          caseId={selectedCase.id}
          onUploadSuccess={handleUploadSuccess}
        />
      )}
    </Box>
  );
};

export default LawyerDashboard;
