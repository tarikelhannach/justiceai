import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Button,
  IconButton,
  Chip,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { usePermissions } from '../hooks/usePermissions';
import SearchBar from './SearchBar';
import api from '../services/api';

const CasesList = () => {
  const { t } = useTranslation();
  const { canEditCase, canDeleteCase, canAssignJudge } = usePermissions();
  
  const [cases, setCases] = useState([]);
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // Dialog states
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState('create'); // 'create', 'edit', 'view'
  const [selectedCase, setSelectedCase] = useState(null);
  const [judges, setJudges] = useState([]);
  
  // Form state
  const [formData, setFormData] = useState({
    case_number: '',
    title: '',
    description: '',
    status: 'pending',
    assigned_judge_id: null,
  });

  useEffect(() => {
    fetchCases();
    fetchJudges();
  }, []);

  const fetchCases = async () => {
    try {
      setLoading(true);
      const response = await api.get('/cases/');
      setCases(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const fetchJudges = async () => {
    try {
      const response = await api.get('/users/judges');
      setJudges(response.data || []);
    } catch (err) {
      console.error('Error fetching judges:', err);
    }
  };

  const handleOpenDialog = (mode, caseItem = null) => {
    setDialogMode(mode);
    setSelectedCase(caseItem);
    if (caseItem) {
      setFormData({
        case_number: caseItem.case_number || '',
        title: caseItem.title || '',
        description: caseItem.description || '',
        status: caseItem.status || 'pending',
        assigned_judge_id: caseItem.assigned_judge_id || null,
      });
    } else {
      setFormData({
        case_number: '',
        title: '',
        description: '',
        status: 'pending',
        assigned_judge_id: null,
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedCase(null);
  };

  const handleSubmit = async () => {
    try {
      if (dialogMode === 'create') {
        await api.post('/cases/', formData);
      } else if (dialogMode === 'edit') {
        await api.put(`/cases/${selectedCase.id}`, formData);
      }
      handleCloseDialog();
      fetchCases();
    } catch (err) {
      setError(err.response?.data?.detail || t('common.error'));
    }
  };

  const handleDelete = async (caseId) => {
    if (window.confirm(t('cases.confirmDelete', '¿Confirmar eliminación?'))) {
      try {
        await api.delete(`/cases/${caseId}`);
        fetchCases();
      } catch (err) {
        setError(err.response?.data?.detail || t('common.error'));
      }
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'warning',
      in_progress: 'info',
      under_review: 'secondary',
      resolved: 'success',
      closed: 'default',
    };
    return colors[status] || 'default';
  };

  const displayCases = searchResults || cases;
  const paginatedCases = displayCases.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight={700}>
          {t('navigation.cases')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog('create')}
        >
          {t('cases.new', 'Nuevo Caso')}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <SearchBar onSearchResults={setSearchResults} />

      <Paper sx={{ mt: 3 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>{t('cases.caseNumber')}</TableCell>
                <TableCell>{t('cases.title')}</TableCell>
                <TableCell>{t('cases.owner')}</TableCell>
                <TableCell>{t('cases.assignedJudge')}</TableCell>
                <TableCell>{t('cases.status.title')}</TableCell>
                <TableCell>{t('cases.createdAt')}</TableCell>
                <TableCell align="right">{t('common.actions')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedCases.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography color="text.secondary" py={3}>
                      {searchResults ? t('search.noResults') : t('dashboard.noCases')}
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                paginatedCases.map((caseItem) => (
                  <TableRow key={caseItem.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight={600}>
                        {caseItem.case_number}
                      </Typography>
                    </TableCell>
                    <TableCell>{caseItem.title}</TableCell>
                    <TableCell>{caseItem.owner?.name || 'N/A'}</TableCell>
                    <TableCell>
                      {caseItem.assigned_judge?.name || t('cases.notAssigned')}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={t(`cases.status.${caseItem.status}`)}
                        color={getStatusColor(caseItem.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(caseItem.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog('view', caseItem)}
                      >
                        <ViewIcon />
                      </IconButton>
                      {canEditCase(caseItem) && (
                        <IconButton
                          size="small"
                          onClick={() => handleOpenDialog('edit', caseItem)}
                        >
                          <EditIcon />
                        </IconButton>
                      )}
                      {canDeleteCase(caseItem) && (
                        <IconButton
                          size="small"
                          onClick={() => handleDelete(caseItem.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={displayCases.length}
          page={page}
          onPageChange={(e, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
          labelRowsPerPage={t('common.rowsPerPage', 'Filas por página')}
        />
      </Paper>

      {/* Dialog for Create/Edit/View */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogMode === 'create' && t('cases.new', 'Nuevo Caso')}
          {dialogMode === 'edit' && t('cases.edit', 'Editar Caso')}
          {dialogMode === 'view' && t('cases.view', 'Ver Caso')}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label={t('cases.caseNumber')}
              value={formData.case_number}
              onChange={(e) => setFormData({ ...formData, case_number: e.target.value })}
              fullWidth
              disabled={dialogMode === 'view' || dialogMode === 'edit'}
              required
            />
            <TextField
              label={t('cases.title')}
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              fullWidth
              disabled={dialogMode === 'view'}
              required
            />
            <TextField
              label={t('cases.description')}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              fullWidth
              multiline
              rows={4}
              disabled={dialogMode === 'view'}
            />
            <TextField
              select
              label={t('cases.status.title')}
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              fullWidth
              disabled={dialogMode === 'view'}
            >
              <MenuItem value="pending">{t('cases.status.pending')}</MenuItem>
              <MenuItem value="in_progress">{t('cases.status.inProgress')}</MenuItem>
              <MenuItem value="under_review">{t('cases.status.underReview')}</MenuItem>
              <MenuItem value="resolved">{t('cases.status.resolved')}</MenuItem>
              <MenuItem value="closed">{t('cases.status.closed')}</MenuItem>
            </TextField>
            {canAssignJudge && (
              <TextField
                select
                label={t('cases.assignedJudge')}
                value={formData.assigned_judge_id || ''}
                onChange={(e) => setFormData({ ...formData, assigned_judge_id: e.target.value || null })}
                fullWidth
                disabled={dialogMode === 'view'}
              >
                <MenuItem value="">{t('cases.notAssigned')}</MenuItem>
                {judges.map((judge) => (
                  <MenuItem key={judge.id} value={judge.id}>
                    {judge.name} ({judge.email})
                  </MenuItem>
                ))}
              </TextField>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>{t('common.cancel')}</Button>
          {dialogMode !== 'view' && (
            <Button onClick={handleSubmit} variant="contained">
              {dialogMode === 'create' ? t('common.create') : t('common.save')}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CasesList;
