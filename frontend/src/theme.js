import { createTheme } from '@mui/material/styles';

export const getDesignTokens = (mode) => ({
  palette: {
    mode,
    ...(mode === 'light'
      ? {
          // Paleta moderna para modo claro
          primary: {
            main: '#2563eb', // Azul moderno
            light: '#60a5fa',
            dark: '#1e40af',
            contrastText: '#ffffff',
          },
          secondary: {
            main: '#7c3aed', // Púrpura elegante
            light: '#a78bfa',
            dark: '#5b21b6',
            contrastText: '#ffffff',
          },
          success: {
            main: '#10b981',
            light: '#34d399',
            dark: '#059669',
          },
          warning: {
            main: '#f59e0b',
            light: '#fbbf24',
            dark: '#d97706',
          },
          error: {
            main: '#ef4444',
            light: '#f87171',
            dark: '#dc2626',
          },
          background: {
            default: '#f8fafc',
            paper: '#ffffff',
            gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          },
          text: {
            primary: '#1e293b',
            secondary: '#64748b',
          },
        }
      : {
          // Paleta moderna para modo oscuro
          primary: {
            main: '#60a5fa',
            light: '#93c5fd',
            dark: '#3b82f6',
            contrastText: '#000000',
          },
          secondary: {
            main: '#a78bfa',
            light: '#c4b5fd',
            dark: '#8b5cf6',
            contrastText: '#000000',
          },
          success: {
            main: '#34d399',
            light: '#6ee7b7',
            dark: '#10b981',
          },
          warning: {
            main: '#fbbf24',
            light: '#fcd34d',
            dark: '#f59e0b',
          },
          error: {
            main: '#f87171',
            light: '#fca5a5',
            dark: '#ef4444',
          },
          background: {
            default: '#0f172a',
            paper: '#1e293b',
            gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          },
          text: {
            primary: '#f1f5f9',
            secondary: '#94a3b8',
          },
        }),
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
      lineHeight: 1.2,
    },
    h2: {
      fontWeight: 700,
      fontSize: '2rem',
      lineHeight: 1.3,
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.75rem',
      lineHeight: 1.3,
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
      lineHeight: 1.4,
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.25rem',
      lineHeight: 1.4,
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
      lineHeight: 1.4,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  shadows: [
    'none',
    '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    ...Array(19).fill('none'),
  ],
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '10px 24px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          },
        },
        contained: {
          background: mode === 'light' 
            ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          '&:hover': {
            background: mode === 'light'
              ? 'linear-gradient(135deg, #5568d3 0%, #63408d 100%)'
              : 'linear-gradient(135deg, #5568d3 0%, #63408d 100%)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: mode === 'light'
            ? '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
            : '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)',
          backdropFilter: 'blur(10px)',
          transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: mode === 'light'
              ? '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
              : '0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.3)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 500,
        },
      },
    },
  },
});

export const createAppTheme = (mode) => createTheme(getDesignTokens(mode));
