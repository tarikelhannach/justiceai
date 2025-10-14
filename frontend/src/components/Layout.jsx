import React, { useState, useMemo } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  useTheme,
  alpha,
  Chip,
  Breadcrumbs,
  Link,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Gavel as GavelIcon,
  Description as DescriptionIcon,
  People as PeopleIcon,
  Settings as SettingsIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  ExitToApp as LogoutIcon,
  Assessment as AuditIcon,
  NavigateNext as NavigateNextIcon,
  Home as HomeIcon,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSelector from './LanguageSelector';
import SkipNavigation from './SkipNavigation';

const drawerWidth = 280;

const getRoleLabel = (role, t) => {
  const roles = {
    admin: t('roles.admin'),
    judge: t('roles.judge'),
    lawyer: t('roles.lawyer'),
    clerk: t('roles.clerk'),
    citizen: t('roles.citizen'),
  };
  return roles[role] || role;
};

const getRoleColor = (role) => {
  const colors = {
    admin: 'error',
    judge: 'primary',
    lawyer: 'success',
    clerk: 'info',
    citizen: 'default',
  };
  return colors[role] || 'default';
};

const Layout = ({ children, onToggleTheme, mode }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useTranslation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems = [
    { text: t('navigation.dashboard'), icon: <DashboardIcon />, path: '/' },
    { text: t('navigation.cases'), icon: <GavelIcon />, path: '/casos' },
    { text: t('navigation.documents'), icon: <DescriptionIcon />, path: '/documentos' },
    { text: t('navigation.users'), icon: <PeopleIcon />, path: '/usuarios' },
    { text: t('navigation.audit'), icon: <AuditIcon />, path: '/auditoria' },
    { text: t('navigation.settings'), icon: <SettingsIcon />, path: '/configuracion' },
  ];

  const breadcrumbs = useMemo(() => {
    const pathnames = location.pathname.split('/').filter((x) => x);
    
    const routes = {
      '': { label: t('navigation.dashboard'), icon: <HomeIcon sx={{ fontSize: 20 }} /> },
      'casos': { label: t('navigation.cases'), icon: <GavelIcon sx={{ fontSize: 20 }} /> },
      'documentos': { label: t('navigation.documents'), icon: <DescriptionIcon sx={{ fontSize: 20 }} /> },
      'usuarios': { label: t('navigation.users'), icon: <PeopleIcon sx={{ fontSize: 20 }} /> },
      'auditoria': { label: t('navigation.audit'), icon: <AuditIcon sx={{ fontSize: 20 }} /> },
      'configuracion': { label: t('navigation.settings'), icon: <SettingsIcon sx={{ fontSize: 20 }} /> },
    };

    const items = [
      { 
        label: routes[''].label, 
        icon: routes[''].icon, 
        path: '/', 
        isHome: true 
      }
    ];

    let currentPath = '';
    pathnames.forEach((pathname) => {
      currentPath += `/${pathname}`;
      const route = routes[pathname];
      if (route) {
        items.push({
          label: route.label,
          icon: route.icon,
          path: currentPath,
          isHome: false
        });
      }
    });

    return items;
  }, [location.pathname, t]);

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo y Título */}
      <Box
        sx={{
          p: 3,
          background: theme.palette.background.gradient,
          color: 'white',
          textAlign: 'center',
        }}
      >
        <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>
          🏛️ {t('branding.appName')}
        </Typography>
        <Typography variant="caption" sx={{ opacity: 0.9 }}>
          {t('branding.country')}
        </Typography>
      </Box>

      <Divider />

      {/* Perfil de Usuario */}
      <Box sx={{ p: 2 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            p: 1.5,
            borderRadius: 2,
            bgcolor: alpha(theme.palette.primary.main, 0.1),
            transition: 'all 0.2s',
            '&:hover': {
              bgcolor: alpha(theme.palette.primary.main, 0.2),
            },
          }}
        >
          <Avatar
            sx={{
              bgcolor: theme.palette.primary.main,
              width: 40,
              height: 40,
              ...(theme.direction === 'rtl' ? { ml: 1.5 } : { mr: 1.5 }),
            }}
          >
            {user?.name?.charAt(0).toUpperCase() || 'U'}
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {user?.name || t('common.user')}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
              {user?.email || ''}
            </Typography>
            <Chip 
              label={getRoleLabel(user?.role, t)}
              size="small"
              color={getRoleColor(user?.role)}
              sx={{ mt: 0.5, height: 20, fontSize: '0.7rem' }}
            />
          </Box>
        </Box>
      </Box>

      <Divider />

      {/* Menú de Navegación */}
      <List sx={{ flex: 1, px: 2, py: 1 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              onClick={() => navigate(item.path)}
              sx={{
                borderRadius: 2,
                '&:hover': {
                  bgcolor: alpha(theme.palette.primary.main, 0.1),
                },
                '&.Mui-selected': {
                  bgcolor: alpha(theme.palette.primary.main, 0.15),
                  '&:hover': {
                    bgcolor: alpha(theme.palette.primary.main, 0.2),
                  },
                },
              }}
              selected={location.pathname === item.path}
            >
              <ListItemIcon sx={{ color: theme.palette.primary.main }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                primaryTypographyProps={{
                  fontSize: '0.95rem',
                  fontWeight: location.pathname === item.path ? 600 : 500,
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Divider />

      {/* Botones de Acción */}
      <Box sx={{ p: 2 }}>
        <ListItemButton
          onClick={async () => {
            await logout();
            navigate('/login');
          }}
          sx={{
            borderRadius: 2,
            '&:hover': {
              bgcolor: alpha(theme.palette.error.main, 0.1),
            },
          }}
        >
          <ListItemIcon sx={{ color: theme.palette.error.main }}>
            <LogoutIcon />
          </ListItemIcon>
          <ListItemText
            primary={t('auth.logout')}
            primaryTypographyProps={{ fontSize: '0.95rem', fontWeight: 500 }}
          />
        </ListItemButton>
      </Box>
    </Box>
  );

  const isRtl = theme.direction === 'rtl';

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Skip Navigation for Accessibility */}
      <SkipNavigation />
      
      {/* AppBar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ...(isRtl 
            ? { mr: { sm: `${drawerWidth}px` } }
            : { ml: { sm: `${drawerWidth}px` } }
          ),
          bgcolor: theme.palette.background.paper,
          color: theme.palette.text.primary,
          boxShadow: theme.shadows[1],
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ 
              ...(isRtl ? { ml: 2 } : { mr: 2 }), 
              display: { sm: 'none' } 
            }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {t('branding.appName')}
          </Typography>
          <LanguageSelector />
          <IconButton onClick={onToggleTheme} color="inherit" sx={{ 
            ...(isRtl ? { mr: 1 } : { ml: 1 })
          }}>
            {mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          anchor={isRtl ? 'right' : 'left'}
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          anchor={isRtl ? 'right' : 'left'}
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              ...(isRtl 
                ? { borderLeft: `1px solid ${alpha(theme.palette.divider, 0.1)}` }
                : { borderRight: `1px solid ${alpha(theme.palette.divider, 0.1)}` }
              ),
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Contenido Principal */}
      <Box
        id="main-content"
        component="main"
        tabIndex={-1}
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          bgcolor: theme.palette.background.default,
          minHeight: '100vh',
          '&:focus': {
            outline: 'none',
          },
        }}
      >
        <Toolbar />
        
        {/* Breadcrumb Navigation */}
        {breadcrumbs.length > 1 && (
          <Box sx={{ mb: 3, mt: 1 }}>
            <Breadcrumbs
              separator={<NavigateNextIcon fontSize="small" />}
              aria-label="breadcrumb"
              sx={{
                '& .MuiBreadcrumbs-separator': {
                  ...(theme.direction === 'rtl' ? { transform: 'rotate(180deg)' } : {})
                }
              }}
            >
              {breadcrumbs.map((item, index) => {
                const isLast = index === breadcrumbs.length - 1;
                
                return isLast ? (
                  <Box
                    key={item.path}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 0.5,
                      color: 'text.primary',
                      fontWeight: 600,
                    }}
                  >
                    {item.icon}
                    <Typography color="text.primary" fontSize="0.875rem" fontWeight={600}>
                      {item.label}
                    </Typography>
                  </Box>
                ) : (
                  <Link
                    key={item.path}
                    underline="hover"
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 0.5,
                      color: 'text.secondary',
                      cursor: 'pointer',
                      transition: 'color 0.2s',
                      '&:hover': {
                        color: 'primary.main',
                      },
                    }}
                    onClick={() => navigate(item.path)}
                  >
                    {item.icon}
                    <Typography fontSize="0.875rem">
                      {item.label}
                    </Typography>
                  </Link>
                );
              })}
            </Breadcrumbs>
          </Box>
        )}
        
        {children}
      </Box>
    </Box>
  );
};

export default Layout;
