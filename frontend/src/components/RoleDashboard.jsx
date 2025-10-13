import React from 'react';
import { usePermissions } from '../hooks/usePermissions';
import AdminDashboard from './AdminDashboard';
import JudgeDashboard from './JudgeDashboard';
import LawyerDashboard from './LawyerDashboard';
import CitizenDashboard from './CitizenDashboard';

const RoleDashboard = () => {
  const { user, ROLES } = usePermissions();

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
      return <AdminDashboard />;
  }
};

export default RoleDashboard;
