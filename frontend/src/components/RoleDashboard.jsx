import React from 'react';
import { usePermissions } from '../hooks/usePermissions';
import AdminDashboard from './AdminDashboard';
import JudgeDashboard from './JudgeDashboard';
import LawyerDashboard from './LawyerDashboard';
import CitizenDashboard from './CitizenDashboard';
import { Box, Typography, Paper } from '@mui/material';
import { useTranslation } from 'react-i18next';

const RoleDashboard = () => {
  const { user, ROLES } = usePermissions();
  const { t } = useTranslation();

  if (!user || !user.role) {
    return null;
  }

  // Render dashboard based on user role
  switch (user.role) {
    case ROLES.ADMIN:
    case ROLES.CLERK:
      return <AdminDashboard />;
    case ROLES.JUDGE:
      return <JudgeDashboard />;
    case ROLES.LAWYER:
      return <LawyerDashboard />;
    case ROLES.CITIZEN:
      return <CitizenDashboard />;
    default:
      return (
        <Box sx={{ p: 3 }}>
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h5" color="error" gutterBottom>
              {t('common.error')}
            </Typography>
            <Typography variant="body1">
              Unauthorized role: {user.role}
            </Typography>
          </Paper>
        </Box>
      );
  }
};

export default RoleDashboard;
