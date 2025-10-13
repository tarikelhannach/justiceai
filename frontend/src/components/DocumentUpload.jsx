import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  LinearProgress,
  Alert,
  IconButton,
  useTheme,
  alpha,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Close as CloseIcon,
  InsertDriveFile as FileIcon,
} from '@mui/icons-material';
import { documentsAPI } from '../services/api';
import { useTranslation } from 'react-i18next';

const DocumentUpload = ({ open, onClose, caseId = null, onUploadSuccess }) => {
  const theme = useTheme();
  const { t } = useTranslation();
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      const maxSize = 50 * 1024 * 1024;
      if (file.size > maxSize) {
        setError(t('documents.fileTooBig'));
        return;
      }
      
      const allowedTypes = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'image/gif',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      ];
      
      if (!allowedTypes.includes(file.type)) {
        setError(t('documents.fileTypeNotAllowed'));
        return;
      }
      
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError(t('documents.selectFile'));
      return;
    }

    try {
      setUploading(true);
      setProgress(30);
      
      const response = await documentsAPI.uploadDocument(selectedFile, caseId);
      
      setProgress(100);
      setSuccess(response.message || t('documents.uploadSuccess'));
      setSelectedFile(null);
      
      if (onUploadSuccess) {
        onUploadSuccess(response);
      }
      
      setTimeout(() => {
        setUploading(false);
        setProgress(0);
        setSuccess(null);
        onClose();
      }, 1500);
      
    } catch (err) {
      setUploading(false);
      setProgress(0);
      setError(err.response?.data?.detail || t('documents.uploadError'));
    }
  };

  const handleClose = () => {
    if (!uploading) {
      setSelectedFile(null);
      setError(null);
      setSuccess(null);
      setProgress(0);
      onClose();
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box display="flex" alignItems="center" gap={1}>
          <UploadIcon color="primary" />
          <Typography variant="h6">{t('documents.upload')}</Typography>
        </Box>
        <IconButton onClick={handleClose} disabled={uploading} size="small">
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        <Box
          sx={{
            border: `2px dashed ${alpha(theme.palette.primary.main, 0.3)}`,
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all 0.3s',
            bgcolor: alpha(theme.palette.primary.main, 0.02),
            '&:hover': {
              borderColor: theme.palette.primary.main,
              bgcolor: alpha(theme.palette.primary.main, 0.05),
            },
          }}
          onClick={() => document.getElementById('file-input').click()}
        >
          <input
            id="file-input"
            type="file"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.gif"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />

          {selectedFile ? (
            <Box display="flex" alignItems="center" justifyContent="center" gap={2}>
              <FileIcon sx={{ fontSize: 48, color: theme.palette.primary.main }} />
              <Box textAlign="left">
                <Typography variant="body1" fontWeight={600}>
                  {selectedFile.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {formatFileSize(selectedFile.size)}
                </Typography>
              </Box>
            </Box>
          ) : (
            <>
              <UploadIcon sx={{ fontSize: 64, color: theme.palette.primary.main, mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                {t('documents.clickToSelect')}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {t('documents.allowedTypes')}
              </Typography>
            </>
          )}
        </Box>

        {uploading && (
          <Box sx={{ mt: 3 }}>
            <LinearProgress variant="determinate" value={progress} sx={{ borderRadius: 1 }} />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              {t('documents.uploading')}... {progress}%
            </Typography>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={uploading}>
          {t('common.cancel')}
        </Button>
        <Button
          onClick={handleUpload}
          variant="contained"
          disabled={!selectedFile || uploading}
          startIcon={<UploadIcon />}
        >
          {uploading ? t('documents.uploading') : t('documents.uploadButton')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentUpload;
