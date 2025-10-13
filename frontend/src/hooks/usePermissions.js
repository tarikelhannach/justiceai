import { useAuth } from '../context/AuthContext';

const ROLES = {
  ADMIN: 'admin',
  JUDGE: 'judge',
  LAWYER: 'lawyer',
  CLERK: 'clerk',
  CITIZEN: 'citizen'
};

const PERMISSIONS = {
  // Case permissions
  VIEW_ALL_CASES: [ROLES.ADMIN, ROLES.CLERK],
  VIEW_OWN_CASES: [ROLES.LAWYER, ROLES.CITIZEN],
  VIEW_ASSIGNED_CASES: [ROLES.JUDGE],
  CREATE_CASE: [ROLES.ADMIN, ROLES.CLERK, ROLES.LAWYER, ROLES.CITIZEN],
  UPDATE_CASE: [ROLES.ADMIN, ROLES.CLERK, ROLES.JUDGE, ROLES.LAWYER, ROLES.CITIZEN],
  DELETE_CASE: [ROLES.ADMIN, ROLES.CLERK],
  
  // Case status permissions
  CHANGE_CASE_STATUS: [ROLES.ADMIN, ROLES.CLERK, ROLES.JUDGE],
  ASSIGN_JUDGE: [ROLES.ADMIN, ROLES.CLERK],
  
  // Document permissions
  UPLOAD_DOCUMENT: [ROLES.ADMIN, ROLES.CLERK, ROLES.JUDGE, ROLES.LAWYER, ROLES.CITIZEN],
  DELETE_DOCUMENT: [ROLES.ADMIN, ROLES.CLERK],
  DOWNLOAD_DOCUMENT: [ROLES.ADMIN, ROLES.CLERK, ROLES.JUDGE, ROLES.LAWYER, ROLES.CITIZEN],
  
  // User management permissions
  MANAGE_USERS: [ROLES.ADMIN],
  VIEW_USERS: [ROLES.ADMIN, ROLES.CLERK],
  APPROVE_USERS: [ROLES.ADMIN],
  
  // Statistics permissions
  VIEW_ALL_STATISTICS: [ROLES.ADMIN, ROLES.CLERK],
  VIEW_OWN_STATISTICS: [ROLES.JUDGE, ROLES.LAWYER],
  
  // Audit permissions
  VIEW_AUDIT_LOG: [ROLES.ADMIN],
};

export const usePermissions = () => {
  const { user } = useAuth();
  
  const hasPermission = (permission) => {
    if (!user || !user.role) return false;
    
    const allowedRoles = PERMISSIONS[permission];
    if (!allowedRoles) return false;
    
    return allowedRoles.includes(user.role);
  };
  
  const hasAnyPermission = (permissions) => {
    return permissions.some(permission => hasPermission(permission));
  };
  
  const hasAllPermissions = (permissions) => {
    return permissions.every(permission => hasPermission(permission));
  };
  
  const hasRole = (role) => {
    if (!user || !user.role) return false;
    return user.role === role;
  };
  
  const hasAnyRole = (roles) => {
    if (!user || !user.role) return false;
    return roles.includes(user.role);
  };
  
  const canViewCase = (caseData) => {
    if (!user || !caseData) return false;
    
    // Admin and clerk can view all cases
    if (hasPermission('VIEW_ALL_CASES')) return true;
    
    // Judge can view assigned cases
    if (hasRole(ROLES.JUDGE) && caseData.assigned_judge_id === user.id) return true;
    
    // Lawyer and citizen can view their own cases
    if (hasAnyRole([ROLES.LAWYER, ROLES.CITIZEN]) && caseData.owner_id === user.id) return true;
    
    return false;
  };
  
  const canUpdateCase = (caseData) => {
    if (!user || !caseData) return false;
    
    // Admin and clerk can update all cases
    if (hasPermission('VIEW_ALL_CASES')) return true;
    
    // Judge can update assigned cases
    if (hasRole(ROLES.JUDGE) && caseData.assigned_judge_id === user.id) return true;
    
    // Lawyer and citizen can update their own cases (limited fields)
    if (hasAnyRole([ROLES.LAWYER, ROLES.CITIZEN]) && caseData.owner_id === user.id) return true;
    
    return false;
  };
  
  const canDeleteCase = (caseData) => {
    if (!user || !caseData) return false;
    return hasPermission('DELETE_CASE');
  };
  
  const canChangeCaseStatus = (caseData) => {
    if (!user || !caseData) return false;
    
    // Admin and clerk can always change status
    if (hasPermission('VIEW_ALL_CASES')) return true;
    
    // Judge can change status of assigned cases
    if (hasRole(ROLES.JUDGE) && caseData.assigned_judge_id === user.id) return true;
    
    return false;
  };
  
  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    hasAnyRole,
    canViewCase,
    canUpdateCase,
    canDeleteCase,
    canChangeCaseStatus,
    user,
    ROLES,
  };
};
